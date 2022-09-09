# For reference ~ https://github.com/pypa/sampleproject/blob/main/setup.py

import pathlib

from setuptools import setup, find_packages


here = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (here / 'README.md').read_text(encoding='utf-8')

setup(
    name='pre-commit-gitlabci-lint',
    version='0.0.1',
    description='',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Emma Doyle',
    author_email='bjd2385.linux@gmail.com',
    keywords='pre-commit, GitLab, CI, continuous integration',
    package_dir={'': 'gitlabci_lint'},
    packages=find_packages(where='gitlabci_lint'),
    python_requires='>=3.10, <4',
    url = 'https://github.com/bjd2385/pre-commit-gitlabci-lint',
    install_requires=[],
    entry_points={
        "console_scripts": ["gitlabci-lint = gitlabci_lint:validateCIConfig"]
    },
    project_urls={  # Optional
        'Bug Reports': 'https://github.com/bjd2385/astronautbot/issues',
        'Source': 'https://github.com/bjd2385/astronautbot'
    },
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
    ]
)
