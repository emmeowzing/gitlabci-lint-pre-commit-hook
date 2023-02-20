# GitLab CI lint pre-commit-hook

This is a [pre-commit](https://pre-commit.com/) hook that uses GitLab's `/api/v4/ci/lint` linting endpoint to validate the contents of `.gitlab-ci.yml` files. This is similar to how CircleCI pre-commit hooks validate that product's required configs: by uploading your config to their API.

```text
$ gitlabci-lint --help
usage: gitlabci-lint [-h] [-c CONFIGS] [-C GITLABCI_LINT_CONFIG] [-B [BASE_URL]] [--version] [-q]

Validate your GitLab CI with GitLab's API endpoint.

options:
  -h, --help            show this help message and exit
  -c CONFIGS, --configs CONFIGS
                        CI Config files to check. (default: .gitlab-ci.yml)
  -C GITLABCI_LINT_CONFIG, --gitlabci-lint-config GITLABCI_LINT_CONFIG
                        Pass parameters via config file. Looks first at '.gitlabci-lint.toml', then '$HOME/.config/gitlabci-lint/config.toml', unless otherwise specified.
  -B [BASE_URL], --base-url [BASE_URL]
                        Base GitLab URL. (default: https://gitlab.com/)
  --version             show program's version number and exit
  -q, -Q, --quiet       Silently fail and pass, without output, unless improperly configured. (default: False)
```

By default, this tool sends your configuration to [https://gitlab.com](https://gitlab.com), though this can be overridden (see below for an example or the help text above).

## Usage

### Requirements

GitLab Lint API now [requires authorization](https://gitlab.com/gitlab-org/gitlab/-/issues/321290).

1. [Create Access Token](https://gitlab.com/-/profile/personal_access_tokens) with `api` scope.
2. Set access token value as a `GITLAB_TOKEN` or `GITLABCI_LINT_TOKEN` environment variable.
3. Ensure Python version available is 3.8 or later.

**Warning** Please note the token should not be shared and if leaked can cause significant harm.

### Example

An example `.pre-commit-config.yaml`:

```yaml
---
repos:
  - repo: https://github.com/bjd2385/pre-commit-gitlabci-lint
    rev: <latest release>
    hooks:
      - id: gitlabci-lint
      # args: [-b, 'https://custom.gitlab.host.com']
```

### Configuration files

No configuration file is required for use. However, if you'd rather specify configuration options in your repo, you may create a config file `.gitlabci-lint.toml` in the repo, or `$HOME/.config/.gitlabci-lint/config.toml`, such as the following.

```toml
[gitlabci-lint]
quiet = false
base-url = "https://gitlab.com"
configs = [ ".gitlab-ci.yml" ]
```

## Development

Install dependencies by running `./scripts/dependencies.sh`. Or, if you already have `yarn` in your path, `yarn install:deps`.

### Releases

Update `setup.py/version`-string and tag this repo's master branch with the same version string (prefixed by '`v`.)
