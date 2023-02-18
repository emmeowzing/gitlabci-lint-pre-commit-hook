"""
Validate your GitLab CI with GitLab's API endpoint.
"""


import argparse
import json
import os
import sys
import configparser
import importlib.metadata as meta
import pathlib

from urllib.error import HTTPError
from urllib.parse import urljoin
from urllib.request import Request, urlopen
from http import HTTPStatus
from functools import partial
from typing import List


__version__ = meta.version('pre-commit-gitlabci-lint')


errprint = partial(print, file=sys.stderr)


if not (token := os.getenv('GITLABCI_LINT_TOKEN')):
    errprint('\'GITLABCI_LINT_TOKEN\' not set, checking for GITLAB_TOKEN.')
    if not (token := os.getenv('GITLAB_TOKEN')):
        errprint('\'GITLAB_TOKEN\' not set. Exiting.')
        sys.exit(1)


def config() -> configparser.ConfigParser:
    """
    Read a config file, if it exists, from standard locations.

    Returns:
        dict: The parsed config file.
    """
    c = configparser.ConfigParser(
        default_section='gitlab-ci'
    )

    config_locations = [
        '.gitlab-ci-lint.toml',
        '$HOME/.config/gitlab-ci-lint/config.toml'
    ]

    for loc in config_locations:
        try:
            if pathlib.Path(loc).exists():
                c.read(pathlib.Path(loc))
                break
        except PermissionError:
            errprint(f'Could not access config file at {loc}, check permissions.')
            sys.exit(1)

    return c


def validateCiConfig(baseUrl: str, configFile: List[str], silent: bool) -> int:
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

    for config in configFile:
        try:
            with open(config, 'r', encoding='utf-8') as f:
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
                    elif lint_output['status'] == 'valid' and lint_output['warnings']:
                        print(f'Config file at \'{configFile}\' is valid, with warnings:', end=' ')
                        for warning in lint_output['warnings']:
                            errprint(warning)
                    else:
                        print(f'Config file at \'{configFile}\' is valid.')
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
        if returnValue == 1:
            break

    return returnValue

if __name__ in ('gitlabci_lint.validate', '__main__'):
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '-c', '--config', action='append',
        help='CI Config files to check. (default: .gitlab-ci.yml)'
    )

    parser.add_argument(
        '-C', '--gitlab-ci-lint-config', action='append',
        help='Pass parameters via config file. Looks first at \'.gitlab-ci-lint.toml\', then \'$HOME/.config/gitlab-ci-lint/config.toml\'. CLI arguments take precendence over config files.'
    )

    parser.add_argument(
        '-b', '-B', '--base_url', nargs='?', default='https://gitlab.com/',
        help='Base GitLab URL. (default: https://gitlab.com/)'
    )

    parser.add_argument(
        '--version', action='version',
        version=f'%(prog)s {__version__}'
    )

    parser.add_argument(
        '-q', '-Q', '--quiet', action='store_true', default=False,
        help='Silently fail and pass, without output, unless improperly configured. '
             '(default: False)'
    )

    args = parser.parse_args()

    base_url = args.base_url
    config_files = args.config
    hook_config_file = args.gitlab_ci_lint_config

    if not config_files:
        # Set default, since there's a bug in argparse that I can't seem to overcome with specifying
        # multiple flags and defaults.
        config_files = ['.gitlab-ci.yml']
    silence = args.quiet

    for config in config_files:
        if (exitCode := validateCiConfig(base_url, config_files, silence)) != os.EX_OK:
            sys.exit(exitCode)

    sys.exit(os.EX_OK)
