#!/bin/bash

cwd=$(cd $(dirname $0); pwd)
appdir=${cwd}/..

source=example/example.py
if [ "$1" != "" ]; then
	source=$1
fi

source ${cwd}/.env.sh
python ${appdir}/py2cpp/bin/analize.py -g data/grammar.lark -s ${source}
