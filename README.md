# `gitlabci-lint` pre-commit hook

[![PyPI version](https://img.shields.io/pypi/v/pre-commit-gitlabci-lint.svg?logo=pypi&style=flat-square)](https://pypi.org/project/pre-commit-gitlabci-lint/)
[![PyPI downloads](https://img.shields.io/pypi/dm/pre-commit-gitlabci-lint?style=flat-square)](https://pypistats.org/packages/pre-commit-gitlabci-lint)

This is a [pre-commit](https://pre-commit.com/) hook that uses GitLab's `/api/v4/ci/lint` linting endpoint to validate the contents of `.gitlab-ci.yml` files. This is similar to CircleCI pre-commit hooks that validate that product's configuration files.

```text
$ gitlabci-lint --help
usage: gitlabci-lint [-h] [-c CONFIGS] [-C GITLABCI_LINT_CONFIG] [-b [BASE_URL]] [-p PROJECT_ID] [--version] [-q]

Validate your GitLab CI with GitLab's API endpoint.

optional arguments:
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

## Use

### Setup

1. [Create an access token](https://gitlab.com/-/profile/personal_access_tokens) with `api` scope.
2. Set access token value in an environment variable named `GITLAB_TOKEN` or `GITLABCI_LINT_TOKEN`.
3. Add the projectId for your gitlab project as a command line argument, or set it in the config file.
4. Ensure the virtualenv Python version is 3.8 or later.

### Configuration

A configuration file is not required for use. However, if you'd rather specify settings in a file that is checked into your project's VCS, you may create a config file located at `/root/of/repo/.gitlabci-lint.toml`, or `$HOME/.config/.gitlabci-lint/config.toml`, such as the following.

```toml
[gitlabci-lint]
quiet = false
base-url = "https://gitlab.com"
project-id = "12345678"
configs = [ ".gitlab-ci.yml" ]
token = "$GITLAB_TOKEN"
```

## Examples

### Shell

```console
$ export GITLAB_TOKEN="$(pass show gitlab-api-key)"
$ gitlabci-lint -p <project_id>
Config file at '.gitlab-ci.yml' is valid.
```

### pre-commit

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

### GitLab CI

Here is an example Gitlab CI job that lints all GitLab CI files in a project on merge requests with naming conventions matching the regex `.*.gitlab-ci.yml`.

```yaml
gitlab-ci-lint:
  stage: test
  image: cimg/base:2023.12
  variables:
    GITLAB_CI_LINT_VERSION: <version>
    YQ_VERSION: 4.40.5
  before_script:
    - set -eo pipefail
    - apt update && apt install -y python3-pip
    - pip install -q --disable-pip-version-check --no-python-version-warning pre-commit-gitlabci-lint=="$GITLAB_CI_LINT_VERSION"
    - |
      wget https://github.com/mikefarah/yq/releases/download/v${YQ_VERSION}/yq_linux_amd64 -O yq
      sudo install yq /usr/local/bin/yq
  script:
    - |+
      mapfile -t _TEMPLATES < <(find . -type f -regex ".*.gitlab-ci.yml")

      for template in "${_TEMPLATES[@]}"; do
          printf "INFO: Considering \"%s\"\\n" "$template"
          _JOB_COUNT="$(yq '... comments="" | to_entries | filter(.key != "include" and .key != "default" and .key != "stages" and .key != "variables" and .key != "workflow" and (.key != ".*") and .key != "cache") | from_entries | length' "$template")"
          if [ "$_JOB_COUNT" -ne "0" ]; then
              printf "INFO: Linting \"%s\"\\n" "$template"
              gitlabci-lint -p "$CI_PROJECT_ID" -b https://"$CI_SERVER_HOST" -c "$template"
          else
              printf "INFO: Skipping \"%s\": no defined jobs.\\n" "$template"
          fi
      done
  tags:
    - small
  rules:
    - $CI_MERGE_REQUEST_TARGET_BRANCH_NAME =~ /^(develop|main)$/ && $SCHEDULE_JOB == null
```
