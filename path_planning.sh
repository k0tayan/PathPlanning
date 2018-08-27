#!/bin/bash
if [ ! -e first ]; then
source ~/.bash_profile
pyenv shell anaconda3-5.0.0
pyenv which python > first
fi
py=$(<first)
$py path_planning.py $1 $2 $3 $4
imgcat output/tmp.png