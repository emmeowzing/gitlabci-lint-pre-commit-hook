"""
Validate your GitLab CI with GitLab's API endpoint.
"""


import argparse
import json
import os
import sys
import toml
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


def validateCiConfig(token: str, baseUrl: str, project_id: str, configs: List[str], silent: bool) -> int:
    """
    Validate the input GitLab CI config against the validation API endpoint.

    Args:
        baseUrl: The location of the GitLab instance.
        project_id: A gitlab project id.
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
            url = urljoin(baseUrl, f'/api/v4/projects/{project_id}/ci/lint')
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

                    if not lint_output['valid']:
                        errprint('=======')
                        for error in lint_output['errors']:
                            errprint(error)
                        returnValue = 1
                        errprint('=======')
                    elif lint_output['valid'] and lint_output['warnings']:
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


def config(conf: Optional[str] =None) -> dict:
    """
    Read a config file, if it exists, from standard locations.

    Returns:
        dict: The parsed config file.
    """
    config_locations = [conf] if conf else [
        '.gitlabci-lint.toml',
        os.path.expandvars('$HOME/.config/gitlabci-lint/config.toml')
    ]

    for loc in config_locations:
        try:
            if pathlib.Path(loc).exists():
                return toml.load(pathlib.Path(loc))
            elif conf:
                errprint(f'Could not locate config file at {loc}, please ensure this file exists.')
                sys.exit(1)
        except PermissionError:
            errprint(f'Could not access config file at {loc}, check permissions.')
            sys.exit(1)

    return {}


def main() -> None:
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
        '-b', '-B', '--base-url', nargs='?', default=default_base_url,
        help=f'Base GitLab URL. (default: {default_base_url})'
    )

    parser.add_argument(
        '-p', '-P', '--project-id',
        help='Project ID to use with the lint API.'
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
    filesystem_config = config(*hook_config_file_CLI) if hook_config_file_CLI else config()

    # Parse a potential config file, with defaults / fallback values matching the CLI's defaults.
    gitlabci_lint_section = filesystem_config.get('gitlabci-lint', {})
    quiet_CONF = gitlabci_lint_section.get('quiet', default_quiet)
    base_url_CONF = os.path.expandvars(gitlabci_lint_section.get('base-url', default_base_url))
    project_id_CONF = os.path.expandvars(gitlabci_lint_section.get('project-id', ''))
    configs_CONF = list(map(os.path.expandvars, gitlabci_lint_section.get('configs', default_configs)))
    token_CONF = os.path.expandvars(gitlabci_lint_section.get('token', ''))

    quiet_CLI = args.quiet
    base_url_CLI = args.base_url
    configs_CLI = args.configs
    project_id_CLI = args.project_id

    # Decide which vars, configuration file or cli, take precendence. Basically how this logic works is, if a setting is
    # enabled in either the config file or via CLI args, it takes precedence.
    quiet = quiet_CONF == 'true' or quiet_CLI
    base_url = base_url_CLI if (base_url_CLI != default_base_url) else (base_url_CONF if (base_url_CONF != default_base_url) else base_url_CLI)
    configs = configs_CLI if (configs_CLI != default_configs) else (configs_CONF if (configs_CONF != default_configs) else configs_CLI)
    project_id = project_id_CLI if project_id_CLI else project_id_CONF
    if not project_id:
        errprint('ERROR: No project ID specified. Please specify a project ID as a command line argument or in the config file.')
        sys.exit(1)

    if not configs:
        # Set default, since there's a bug in argparse that I can't seem to overcome with specifying
        # multiple flags and defaults.
        configs = ['.gitlab-ci.yml']

    if token_CONF:
        token = os.path.expandvars(token_CONF)
    elif not ((token := os.getenv('GITLABCI_LINT_TOKEN')) or (token := os.getenv('GITLAB_TOKEN'))):
        errprint('ERROR: Neither \'GITLABCI_LINT_TOKEN\' nor \'GITLAB_TOKEN\' set.')
        sys.exit(1)

    sys.exit(validateCiConfig(token, base_url, project_id, configs, quiet))


if __name__ == '__main__':
    main()