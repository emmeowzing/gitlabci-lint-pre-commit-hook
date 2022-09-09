pre-commit-gitlabci-lint
------------------------

This is a [pre-commit hook](https://pre-commit.com/). Uses the `/api/v4/ci/lint` lint endpoint to validate the contents of your `.gitlab-ci.yml` file, in a similar fashion that CircleCI pre-commit hooks validate by uploading your config to an endpoint.

By default, this tool sends your configuration to https://gitlab.com, though this can be overridden (see below).

## Usage

GitLab Lint API now [requires authorization](https://gitlab.com/gitlab-org/gitlab/-/issues/321290).

1. [Create Access Token](https://gitlab.com/-/profile/personal_access_tokens) with `api` scope.
2. Set access token value as `GITLAB_TOKEN` environment variable.

**Warning** Please note the token should not be shared and if leaked can cause significant harm.

An example `.pre-commit-config.yaml`:

```yaml
---
repos:
  - repo: https://github.com/kadrach/pre-commit-gitlabci-lint
    rev: <latest release>
    hooks:
      - id: gitlabci-lint
      # args: ["https://custom.gitlab.host.com"]
```