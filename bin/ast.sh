#!/bin/bash

cwd=$(cd $(dirname $0); pwd)
appdir=${cwd}/..

source ${cwd}/.env.sh
python ${appdir}/py2cpp/app/ast_check.py ${appdir}/data/grammar.lark
