#!/bin/bash

cwd=$(cd $(dirname $0); pwd)
appdir=${cwd}/..

if [ -z ${PYTHONDONTWRITEBYTECODE} ]; then
	export PYTHONDONTWRITEBYTECODE=1
fi

if [ -z ${PYTHONPATH} ]; then
	export PYTHONPATH=${appdir}:${appdir}/vendor
else
	export PYTHONPATH=${appdir}:${appdir}/vendor:${PYTHONPATH}
fi
