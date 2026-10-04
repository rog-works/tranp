#!/bin/bash

cwd=$(cd $(dirname $0); pwd)
appdir=${cwd}/..

source ${cwd}/.env.sh

if [ "$1" == "-h" ]; then
	cat << EOS
# Usage
$ bin/test.sh [-l module_name] [-c case_name] [-v] [-p]
# Examples
$ bin/test.sh -l py2cpp
$ bin/test.sh -l reflections -c type_of
$ bin/test.sh -l py2cpp -v
$ bin/test.sh -l py2cpp -p
EOS
	exit
fi

target=
if [ "$1" == "-l" ]; then
	shift
	peco_opt=
	if [ "${1}" != "" -a "${1:0:1}" != "-" ]; then
		peco_opt="--query ${1}"
		shift
	fi

	module=$(find ./tests/ -name 'test_*.py' | egrep -v 'fixtures|vendor' | peco ${peco_opt})
	target=$(echo "$module" | sed -e 's/^.\///g')
	target=$(echo "$target" | sed -e 's/\//\./g')
	target=$(echo "$target" | sed -e 's/\.py$//g')

	if [ "$1" == "-c" ]; then
		shift
		peco_opt=
		if [ "${1}" != "" -a "${1:0:1}" != "-" ]; then
			peco_opt="--query ${1}"
			shift
		fi

		case=$(python tranp/app/test/case_discovery.py ${module} | cat - | peco ${peco_opt})
		target="${target}.${case}"
	fi
fi

while [ $# -gt 0 ]; do
	if [ "${1}" == "-v" ]; then
		export TRANPVERBOSE=1
	elif [ "${1}" == "-p" ]; then
		export TRANPPROFILE=1
	elif [ "${1}" == "--index" ]; then
		shift
		export TRANPTESTINDEX=$1
	fi
	shift
done


if [ "$target" == "" ]; then
	echo python -m unittest discover tests/
	python -m unittest discover tests/
else
	echo python -m unittest ${target} ${profiler}
	python -m unittest ${target} ${profiler}
fi
