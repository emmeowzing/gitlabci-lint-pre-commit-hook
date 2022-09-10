"""
Validate your GitLab CI with GitLab's API endpoint.
"""


import argparse
import json
import os
import sys

from urllib.error import HTTPError
from urllib.parse import urljoin
from urllib.request import Request, urlopen
from http import HTTPStatus
from functools import partial


__version__ = '0.0.5'


if not (token := os.getenv('GITLAB_TOKEN')):
    print('\'GITLAB_TOKEN\' not set. Exiting.')
    sys.exit(1)


errprint = partial(print, file=sys.stderr)


def validateCiConfig(baseUrl: str, configFile: str, silent: bool) -> int:
    """
    Validate the input GitLab CI config against the validation API endpoint.

    Args:
        baseUrl: The location of the GitLab instance.
        configFile: The GitLab CI file to validate.
        silent: Whether or not to output text on success or failure, unless improperly configured.
                Allows the use of exit codes in scripts without redirecting stdout.

    Returns:
        An exit code, zero if successful and the CI config is valid.
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
        headers = {
            'Content-Type': 'application/json',
            'Content-Length': str(len(data))
        }

        # Get around mypy typing issue with if statement.
        if token:
            headers['PRIVATE-TOKEN'] = token

        try:
            request = Request(
                url,
                data.encode('utf-8'),
                headers=headers,
            )

            if not silent:
                with urlopen(request) as response:
                    lint_output = json.loads(response.read())

                if lint_output['status'] == 'invalid':
                    errprint('=======')
                    for error in lint_output['errors']:
                        errprint(error)
                    returnValue = 1
                    errprint('=======')
                else:
                    print(f'Config file at {configFile} is valid.')
            else:
                with urlopen(request) as response:
                    lint_output = json.loads(response.read())

                if lint_output['status'] == 'invalid':
                    returnValue = 1

        except HTTPError as exc:
            errprint(f'Error connecting to Gitlab: {exc}')

            if exc.code == HTTPStatus.UNAUTHORIZED:
                errprint(
                    'The lint endpoint requires authentication.'
                    'Please check value of \'GITLAB_TOKEN\' environment variable'
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
        '-b', '-B', '--base_url', nargs='?', default='https://gitlab.com/',
        help='Base GitLab URL.'
    )

    parser.add_argument(
        '-c', '-C', '--config', nargs='?', default='.gitlab-ci.yml',
        help='CI Config file to check.'
    )

    parser.add_argument(
        '--version', action='version',
        version=f'%(prog)s {__version__}'
    )

    parser.add_argument(
        '-q', '-Q', '--quiet', action='store_true', default=False,
        help='Silently fail and pass, without output, unless improperly configured.'
    )

    args = parser.parse_args()

    base_url = args.base_url
    config_file = args.config
    silence = args.quiet

    if (exitCode := validateCiConfig(base_url, config_file, silence)) == os.EX_OK:
        # Optionally could print message.
        pass

    sys.exit(exitCode)
