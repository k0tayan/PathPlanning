#!/bin/bash
if [ ! -e first ]; then
source ~/.bash_profile
pyenv shell anaconda3-5.0.0
pyenv which python > first
fi
py=$(<first)

$py detection.py