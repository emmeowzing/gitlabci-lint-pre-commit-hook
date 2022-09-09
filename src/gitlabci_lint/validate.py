"""
Validate your GitLab CI with GitLab's API endpoint.
"""


from typing import Any

import argparse
import json
import os
import sys
import pathlib

from urllib.error import HTTPError
from urllib.parse import urljoin
from urllib.request import Request, urlopen
from http import HTTPStatus
from functools import partial


if not (token := os.getenv('GITLAB_TOKEN')):
    print('\'GITLAB_TOKEN\' not set. Exiting.')
    sys.exit(1)

DEBUG = bool(os.getenv('GITLAB_DEBUG'))


errprint = partial(print, file=sys.stderr)


def validateCiConfig(baseUrl: str, configFile: str) -> int:
    """
    Validate the input GitLab CI config against the validation API endpoint.

    Args:
        baseUrl: The location of the GitLab instance.
        configFile: The GitLab CI file to validate.
    """
    returnValue = 0

    try:
        with open(configFile, 'r', encoding='utf-8') as f:
            data = json.dumps(
                {
                    'content': f.read()
                }
            )
    except (FileNotFoundError, PermissionError):
        errprint(f'Cannot open {configFile}')
        returnValue = 1
    else:
        url = urljoin(baseUrl, '/api/v4/ci/lint')
        msg_using_linter = f'Using linter: {url}'
        headers = {
            'Content-Type': 'application/json',
            'Content-Length': str(len(data))
        }

        if token:
            headers['PRIVATE-TOKEN'] = token
            if DEBUG:
                msg_using_linter += f' with token {token}'
        print(msg_using_linter)

        try:
            request = Request(
                url,
                data.encode('utf-8'),
                headers=headers,
            )

            with urlopen(request) as response:
                lint_output = json.loads(response.read())

            if lint_output['status'] == 'invalid':
                errprint('=======')
                for error in lint_output['errors']:
                    errprint(error)
                returnValue = 1
                errprint('=======')

        except HTTPError as exc:
            errprint(f'Error connecting to Gitlab: {exc}')

            if exc.code == HTTPStatus.UNAUTHORIZED:
                print(
                    'The lint endpoint requires authentication.'
                    'Please check value of \'GITLAB_TOKEN\' environment variable',
                    file=sys.stderr
                )
            else:
                errprint(f'Failed with reason \'{exc.reason}\'')

            returnValue = 1
    return returnValue


if __name__ in ('gitlabci_lint.validate', '__main__'):
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument(
        '-b', '--base_url', nargs='?', default='https://gitlab.com/',
        help='Base GitLab URL.'
    )

    parser.add_argument(
        '-c', '--config', nargs='?', default='.gitlab-ci.yml',
        help='CI Config file to check.'
    )

    args = parser.parse_args()

    base_url = args.base_url
    config_file = args.config

    sys.exit(validateCiConfig(base_url, config_file))
