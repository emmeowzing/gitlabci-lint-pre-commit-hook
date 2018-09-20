from setuptools import setup


setup(
    name="pre-commit-gitlabci-lint",
    packages=["gitlabci_lint"],
    entry_points={"console_scripts": ["gitlabci-lint = gitlabci_lint:main"]},
)
