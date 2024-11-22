#!/bin/bash

cwd=$(cd $(dirname $0); pwd)
appdir=${cwd}/..

target=
if [ "$1" == "-l" ]; then
	target=$(find ./ -name 'test_*.py' | egrep -v 'fixtures|vendor' | peco)
	target=$(echo "$target" | sed -e 's/^.\///g')
	target=$(echo "$target" | sed -e 's/\//\./g')
	target=$(echo "$target" | sed -e 's/\.py$//g')
	shift
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
