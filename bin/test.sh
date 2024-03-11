#!/bin/bash

cwd=$(cd $(dirname $0); pwd)
appdir=${cwd}/..

target=
if [ "$1" != "" ]; then
	target=$1
fi

if [ "$2" != "" ]; then
	target="$1::$2"
fi

if [ "$3" != "" ]; then
	target="$1::$2::$3"
fi

source ${cwd}/.env.sh

if [ "$target" == "" ]; then
	pytest ${appdir}/tests/unit --ignore-glob=**/fixtures/*
else
	pytest ${target}
fi
