#!/bin/bash

cwd=$(cd $(dirname $0); pwd)
appdir=${cwd}/..

for arg in "$@"; do
	if [ "${arg}" == "-v" ]; then
		export PYVERBOSE=1
	fi
done

source ${cwd}/.env.sh
python ${appdir}/rogw/tranp/bin/ast_check.py $*
