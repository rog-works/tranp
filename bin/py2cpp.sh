#!/bin/bash

cwd=$(cd $(dirname $0); pwd)
appdir=${cwd}/..

target=example/example.py
if [ "$1" != "" ]; then
	target=$1
fi

source ${cwd}/.env.sh
python ${appdir}/py2cpp/app/handler.py data/grammar.lark ${target}
