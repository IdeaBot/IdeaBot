#!/bin/bash
# setup an up to date environment for development

# do regular init
./scripts/init.sh

# use most recent commits from submodules
git submodule foreach "git checkout master && git pull"
