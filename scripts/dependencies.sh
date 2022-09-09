#! /bin/bash

asdf plugin add nodejs https://github.com/asdf-vm/asdf-nodejs.git
asdf plugin-add yarn

asdf install

if [ "$(conda info --envs --json | jq -r '.envs[]' | awk '/(gitlab-ci-lint)$/')" = "" ]; then
    conda create -y -n gitlab-ci-lint python=3.10
fi

#conda activate gitlab-ci-lint
#pip install setupext_janitor pylint mypy
