#!/bin/bash

cwd=$(cd $(dirname $0); pwd)
appdir=${cwd}/..

export PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH=${appdir}:${appdir}/vendor
