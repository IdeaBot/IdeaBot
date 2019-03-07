#!/bin/bash
# this also works for updating

# init submodules
git submodule update --init

# install requirements
sudo pip3 install -r requirements.txt
sudo pip3 install -r addons/**/requirements.txt
