#!/bin/bash

cwd=$(cd $(dirname $0); pwd)
appdir=${cwd}/..

rm -fr ${appdir}/dist
rm -fr ${appdir}/tranp.egg-info

version=`cat ${appdir}/pyproject.toml | grep version | awk '{print $3}'`
if [ $# -eq 1 ] && [ "\"$1\"" == "${version}" ]; then
	python -m build && python -m twine upload ${appdir}/dist/*
fi
