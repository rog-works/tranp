#!/bin/bash

cwd=$(cd $(dirname $0); pwd)
appdir=${cwd}/..

source ${cwd}/.env.sh

python ${appdir}/tranp/app/bin/di_defs.py $*
