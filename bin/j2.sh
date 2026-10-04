#!/bin/bash

cwd=$(cd $(dirname $0); pwd)
appdir=${cwd}/..

source ${cwd}/.env.sh

python tranp/app/bin/j2_check.py $*
