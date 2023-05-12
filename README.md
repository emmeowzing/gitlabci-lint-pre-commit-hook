# GitLab CI lint pre-commit hook

This is a [pre-commit](https://pre-commit.com/) hook that uses GitLab's `/api/v4/ci/lint` linting endpoint to validate the contents of `.gitlab-ci.yml` files. This is similar to CircleCI pre-commit hooks that validate that product's configuration files.

```text
$ gitlabci-lint --help
usage: gitlabci-lint [-h] [-c CONFIGS] [-C GITLABCI_LINT_CONFIG] [-b [BASE_URL]] [--version] [-q]

Validate your GitLab CI with GitLab's API endpoint.

options:
  -h, --help            show this help message and exit
  -c CONFIGS, --configs CONFIGS
                        CI Config files to check. (default: .gitlab-ci.yml)
  -C GITLABCI_LINT_CONFIG, --gitlabci-lint-config GITLABCI_LINT_CONFIG
                        Pass parameters via config file. Looks first at '.gitlabci-lint.toml', then '$HOME/.config/gitlabci-lint/config.toml', unless otherwise specified.
  -b [BASE_URL], -B [BASE_URL], --base-url [BASE_URL]
                        Base GitLab URL. (default: https://gitlab.com/)
  -p PROJECT_ID, -P PROJECT_ID, --project-id PROJECT_ID
                        Project ID to use with the lint API.
  --version             show program's version number and exit
  -q, -Q, --quiet       Silently fail and pass, without output, unless improperly configured. (default: False)
```

## Install

```shell
pip install pre-commit-gitlabci-lint
```

## Usage

### Setup

1. [Create an access token](https://gitlab.com/-/profile/personal_access_tokens) with `api` scope.
2. Set access token value in an environment variable named `GITLAB_TOKEN` or `GITLABCI_LINT_TOKEN`.
3. Add the projectId for your gitlab project as a command line argument, or set it in the config file.
4. Ensure the virtualenv Python version is 3.8 or later.

### Example

An example `.pre-commit-config.yaml`:

```yaml
---
repos:
  - repo: https://github.com/bjd2385/pre-commit-gitlabci-lint
    rev: <latest release>
    hooks:
      - id: gitlabci-lint
      # args: [-b, 'https://custom.gitlab.host.com', '-p', '12345678']
```

### Use configuration files

No configuration file is required for use. However, if you'd rather specify settings in your repo, you may create a config file located at `/root/of/repo/.gitlabci-lint.toml`, or `$HOME/.config/.gitlabci-lint/config.toml`, such as the following.

```toml
[gitlabci-lint]
quiet = false
base-url = "https://gitlab.com"
project-id = "12345678"
configs = [ ".gitlab-ci.yml" ]
token = "$GITLAB_TOKEN"
```