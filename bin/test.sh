#!/bin/bash

cwd=$(cd $(dirname $0); pwd)
appdir=${cwd}/..

target=
if [ "$1" != "" ]; then
	target=$(echo "$1" | sed -e 's/\//\./g')
	target=$(echo "$target" | sed -e 's/\.py$//g')
fi

if [ "$2" != "" ]; then
	target=${target}.$2
fi

if [ "$3" != "" ]; then
	target=${target}.$3
fi

source ${cwd}/.env.sh

if [ "$target" == "" ]; then
	echo python -m unittest discover ${appdir}/tests/
	python -m unittest discover ${appdir}/tests/
else
	echo python -m unittest ${target}
	python -m unittest ${target}
fi
