#!/bin/bash

cwd=$(cd $(dirname $0); pwd)
appdir=${cwd}/..

source ${cwd}/.env.sh

target=
if [ "$1" == "-l" ]; then
	shift
	peco_opt=
	if [ "${1}" != "" -a "${1:0:1}" != "-" ]; then
		peco_opt="--query ${1}"
		shift
	fi

	target=$(find tests/ -name 'test_*.py' | egrep -v 'fixtures|vendor' | peco ${peco_opt})
	target=$(echo "$target" | sed -e 's/^.\///g')
	target=$(echo "$target" | sed -e 's/\//\./g')
	target=$(echo "$target" | sed -e 's/\.py$//g')
fi

if [ "$1" == "-d" ]; then
	shift
	cd ${appdir} && python tranp/app/bin/profile_diff.py $*
else
	echo python tranp/app/bin/profiler.py
	cd ${appdir} && python tranp/app/bin/profiler.py -t "${target}" $*
fi
