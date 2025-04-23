#!/bin/bash

cwd=$(cd $(dirname $0); pwd)
appdir=${cwd}/..

source ${cwd}/.env.sh

if [ "$1" != "-l" ]; then
	echo '### Usage'
	echo bin/profile.sh -l
	echo bin/profile.sh -l '${query}'
	exit
fi

target=$1
shift
peco_opt=
if [ "${1}" != "" -a "${1:0:1}" != "-" ]; then
	peco_opt="--query ${1}"
	shift
fi

target=$(find ./ -name 'test_*.py' | | egrep -v 'fixtures|vendor' | peco ${peco_opt})
target=$(echo "$target" | sed -e 's/^.\///g')
target=$(echo "$target" | sed -e 's/\//\./g')
target=$(echo "$target" | sed -e 's/\.py$//g')

echo python -m unittest ${target}
cd ${appdir} && ./vendor/bin/pyinstrument -m unittest ${target}
