#!/bin/bash

cwd=$(cd $(dirname $0); pwd)
appdir=${cwd}/..

version=`cat ${appdir}/pyproject.toml | grep version | awk '{print $3}'`
if [ "${!#}" == "${version}" ]; then
	rm -fr ${appdir}/dist
	python -m build python && python -m twine upload ${appdir}/dist/*
fi
