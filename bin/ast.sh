#!/bin/bash

cwd=$(cd $(dirname $0); pwd)
appdir=${cwd}/..

source ${cwd}/.env.sh

for arg in "$@"; do
	if [ "${arg}" == "-v" ]; then
		export TRANPVERBOSE=1
	fi
done

python ${appdir}/tranp/app/bin/ast_check.py $*
