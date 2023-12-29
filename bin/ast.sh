#!/bin/bash

cwd=$(cd $(dirname $0); pwd)
appdir=${cwd}/..

source ${cwd}/.env.sh
python ${appdir}/py2cpp/bin/ast_check.py -g data/grammar.lark $*
