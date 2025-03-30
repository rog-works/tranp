#!/bin/bash

cwd=$(cd $(dirname $0); pwd)
appdir=${cwd}/..

target=
if [ "$1" == "-l" ]; then
	shift
	peco_opt=
	if [ "${1}" != "" -a "${1:0:1}" != "-" ]; then
		peco_opt="--query ${1}"
		shift
	fi

	target=$(find ./ -name 'test_*.py' | egrep -v 'fixtures|vendor' | peco ${peco_opt})
	target=$(echo "$target" | sed -e 's/^.\///g')
	target=$(echo "$target" | sed -e 's/\//\./g')
	target=$(echo "$target" | sed -e 's/\.py$//g')
fi

profiler=
if [ "$1" == "-p" ]; then
	profiler=--
fi

source ${cwd}/.env.sh

if [ "$target" == "" ]; then
	echo python -m unittest discover ${appdir}/tests/
	python -m unittest discover ${appdir}/tests/
else
	echo python -m unittest ${target} ${profiler}
	python -m unittest ${target} ${profiler}
fi
