#!/bin/bash

cwd=$(cd $(dirname $0); pwd)
appdir=${cwd}/..

source=example/example.py
if [ "$1" != "" ]; then
	source=$1
fi

template_dir=example/template
if [ "$2" != "" ]; then
	template_dir=$2
fi

source ${cwd}/.env.sh
python ${appdir}/tranp/bin/transpile.py -g data/grammar.lark -s ${source} -t ${template_dir}
