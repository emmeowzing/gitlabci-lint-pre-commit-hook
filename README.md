# pre-commit-gitlabci-lint

This is a [pre-commit hook](https://pre-commit.com/). Uses the `/api/v4/ci/lint` lint endpoint to validate the contents of your `.gitlab-ci.yml` file. By default, sends your configuration to https://gitlab.com, but this can be overridden, see below.

An example `.pre-commit-config.yaml`:

```yaml
---
repos:
  - repo: https://github.com/kadrach/pre-commit-gitlabci-lint
    rev: master
    hooks:
      - id: gitlabci-lint
      # args: ["https://custom.gitlab.host.com"]
```

