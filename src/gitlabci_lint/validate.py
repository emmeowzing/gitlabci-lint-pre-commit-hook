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
from typing import List, Optional


__version__ = meta.version('pre-commit-gitlabci-lint')


errprint = partial(print, file=sys.stderr)

default_config_section = 'gitlabci-lint'
default_base_url: str = 'https://gitlab.com/'
default_quiet: bool = False
default_configs: List[str] = list()


def validateCiConfig(token: str, baseUrl: str, configs: List[str], silent: bool) -> int:
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

    for config in configs:
        try:
            with open(config, 'r', encoding='utf-8') as f:
                data = json.dumps(
                    {
                        'content': f.read()
                    }
                )
        except (FileNotFoundError, PermissionError):
            errprint(f'Cannot open {config}')
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

                if silent:
                    # Lint quietly.
                    with urlopen(request) as response:
                        lint_output = json.loads(response.read())

                    if lint_output['status'] == 'invalid':
                        returnValue = 1
                else:
                    # Lint verbosely.
                    with urlopen(request) as response:
                        lint_output = json.loads(response.read())

                    if lint_output['status'] == 'invalid':
                        errprint('=======')
                        for error in lint_output['errors']:
                            errprint(error)
                        returnValue = 1
                        errprint('=======')
                    elif lint_output['status'] == 'valid' and lint_output['warnings']:
                        print(f'Config file at \'{config}\' is valid, with warnings:', end=' ')
                        for warning in lint_output['warnings']:
                            errprint(warning)
                    else:
                        print(f'Config file at \'{config}\' is valid.')

            except HTTPError as exc:
                errprint(f'Error connecting to Gitlab: {exc}')

                if exc.code == HTTPStatus.UNAUTHORIZED:
                    errprint(
                        'The lint endpoint requires authentication. '
                        'Please check value of \'GITLAB_TOKEN\' environment variable.'
                    )
                else:
                    errprint(f'Failed with reason \'{exc.reason}\'')

                returnValue = 1
        if returnValue == 1:
            break

    return returnValue


def config(conf: Optional[str] =None) -> configparser.ConfigParser:
    """
    Read a config file, if it exists, from standard locations.

    Returns:
        dict: The parsed config file.
    """
    c = configparser.ConfigParser(
        default_section=default_config_section
    )

    config_locations = [conf] if conf else [
        '.gitlabci-lint.toml',
        os.path.expandvars('$HOME/.config/gitlabci-lint/config.toml')
    ]

    print(config_locations)

    for loc in config_locations:
        try:
            if pathlib.Path(loc).exists():
                c.read(pathlib.Path(loc))
                break
            elif conf:
                errprint(f'Could not locate config file at {loc}, please ensure this file exists.')
                sys.exit(1)
        except PermissionError:
            errprint(f'Could not access config file at {loc}, check permissions.')
            sys.exit(1)

    return c


def cli() -> None:
    """
    Set up CLI for gitlabci-lint pre-commit hook.
    """
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '-c', '--configs', action='append', default=list(),
        help='CI Config files to check. (default: .gitlab-ci.yml)'
    )

    parser.add_argument(
        '-C', '--gitlabci-lint-config', nargs=1, default=None,
        help='Pass parameters via config file. Looks first at \'.gitlabci-lint.toml\', then \'$HOME/.config/gitlabci-lint/config.toml\', unless otherwise specified.'
    )

    parser.add_argument(
        '-B', '--base-url', nargs='?', default=default_base_url,
        help=f'Base GitLab URL. (default: {default_base_url})'
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

    # If a gitlabci-lint config was specified via CLI, override the default search locations.
    hook_config_file_CLI = args.gitlabci_lint_config
    if hook_config_file_CLI:
        filesystem_config = config(*hook_config_file_CLI)
    else:
        filesystem_config = config()

    # Parse a potential config file, with defaults / fallback values matching the CLI's defaults.
    quiet_CONF = filesystem_config[default_config_section].get('quiet', str(default_quiet).lower())
    base_url_CONF = os.path.expandvars(filesystem_config[default_config_section].get('base-url', default_base_url))
    configs_CONF = list(
        map(
            os.path.expandvars,
            json.loads(filesystem_config[default_config_section].get('configs', str(default_configs)))
        )
    )
    token_CONF = os.path.expandvars(filesystem_config[default_config_section].get('configs', None))

    quiet_CLI = args.quiet
    base_url_CLI = args.base_url
    configs_CLI = args.configs

    # Decide which vars, configuration file or cli, take precendence. Basically how this logic works is, if a setting is
    # enabled in either the config file or via CLI args, it takes precedence.
    quiet = quiet_CONF == 'true' or quiet_CLI
    base_url = base_url_CLI if (base_url_CLI != default_base_url) else (base_url_CONF if (base_url_CONF != default_base_url) else base_url_CLI)
    configs = configs_CLI if (configs_CLI != default_configs) else (configs_CONF if (configs_CONF != default_configs) else configs_CLI)

    if not configs:
        # Set default, since there's a bug in argparse that I can't seem to overcome with specifying
        # multiple flags and defaults.
        configs = ['.gitlab-ci.yml']

    token: Optional[str]
    if token_CONF:
        token = os.path.expandvars(token_CONF)
    elif not ((token := os.getenv('GITLABCI_LINT_TOKEN')) or (token := os.getenv('GITLAB_TOKEN'))):
        errprint('ERROR: Neither \'GITLABCI_LINT_TOKEN\' nor \'GITLAB_TOKEN\' set.')
        sys.exit(1)

    if (exitCode := validateCiConfig(token, base_url, configs, quiet)) != os.EX_OK:
            sys.exit(exitCode)

    sys.exit(os.EX_OK)


if __name__ == '__main__':
    cli()
