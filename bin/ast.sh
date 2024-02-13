#!/bin/bash

cwd=$(cd $(dirname $0); pwd)
appdir=${cwd}/..

source ${cwd}/.env.sh
python ${appdir}/rogw/tranp/bin/ast_check.py -g data/grammar.lark $*
