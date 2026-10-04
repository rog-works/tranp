#!/bin/bash

cwd=$(cd $(dirname $0); pwd)
appdir=${cwd}/..

rm -fr dist/
rm -fr tranp.egg-info/

version=`cat pyproject.toml | grep version | awk '{print $3}'`
if [ $# -eq 1 ] && [ "\"$1\"" == "${version}" ]; then
	python -m build && python -m twine upload dist/*
fi
