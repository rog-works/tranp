#!/bin/bash

cwd=$(cd $(dirname $0); pwd)
appdir=${cwd}/..

if [ "$1" == '-d' ]; then
	rm -fr ${appdir}/.cache/tranp
fi
