# For reference ~ https://github.com/pypa/sampleproject/blob/main/setup.py

import pathlib

from setuptools import setup, find_packages

# Cf. https://github.com/dave-shawley/setupext-janitor#installation
try:
   from setupext_janitor import janitor
   cleanCommand = janitor.CleanCommand
except ImportError:
   cleanCommand = None

cmd_classes = {}
if cleanCommand is not None:
   cmd_classes['clean'] = cleanCommand


here = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (here / 'README.md').read_text(encoding='utf-8')

setup(
    name='pre-commit-gitlabci-lint',
    version='1.0.0',
    description='Validate your GitLab CI with GitLab\'s API endpoint.',
    cmdclass=cmd_classes,
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Emma Doyle',
    author_email='bjd2385.linux@gmail.com',
    keywords='pre-commit, GitLab, CI, continuous integration',
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    python_requires='>=3.10, <4',
    url = 'https://github.com/bjd2385/pre-commit-gitlabci-lint',
    install_requires=[],
    entry_points={
        "console_scripts": ["gitlabci-lint = gitlabci_lint.validate:validateCiConfig"]
    },
    project_urls={  # Optional
        'Bug Reports': 'https://github.com/bjd2385/pre-commit-gitlabci-lint/issues',
        'Source': 'https://github.com/bjd2385/pre-commit-gitlabci-lint'
    },
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
    ]
)
