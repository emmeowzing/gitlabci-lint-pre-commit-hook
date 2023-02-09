# GitLab CI lint pre-commit-hook

This is a [pre-commit hook](https://pre-commit.com/) that uses GitLab's `/api/v4/ci/lint` lint endpoint to validate the contents of `.gitlab-ci.yml` files. This is similar in fashion to how CircleCI pre-commit hooks validate that product's required configs, which is by uploading your config to an endpoint.

```shell
$ gitlabci-lint --help
usage: gitlabci-lint [-h] [-c CONFIG] [-b [BASE_URL]] [--version] [-q]

Validate your GitLab CI with GitLab's API endpoint.

options:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        CI Config files to check. (default: .gitlab-ci.yml)
  -b [BASE_URL], -B [BASE_URL], --base_url [BASE_URL]
                        Base GitLab URL. (default: https://gitlab.com/)
  --version             show program's version number and exit
  -q, -Q, --quiet       Silently fail and pass, without output, unless improperly configured. (default: False)
```

By default, this tool sends your configuration to https://gitlab.com, though this can be overridden (see below).

This tool has been extended and adapted from [kadrach's](https://github.com/kadrach/pre-commit-gitlabci-lint) implementation (cf. the [license](LICENSE)).

## Usage

### Requirements

GitLab Lint API now [requires authorization](https://gitlab.com/gitlab-org/gitlab/-/issues/321290).

1. [Create Access Token](https://gitlab.com/-/profile/personal_access_tokens) with `api` scope.
2. Set access token value as `GITLAB_TOKEN` environment variable.
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

## Development

Install dependencies by running `./scripts/dependencies.sh`. Or, if you already have `yarn` in your path, `yarn install:deps`.

### Releases

Update `src/gitlabci_lint/validate.py/__version__`, `setup.py/version`-string, and tag this repo's master branch with the same version string (prefixed by '`v`.)
