#!/bin/bash

cwd=$(cd $(dirname $0); pwd)
appdir=${cwd}/..

source ${cwd}/.env.sh
python ${appdir}/tranp/bin/analyze.py -g data/grammar.lark $*
