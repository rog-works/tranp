#!/bin/bash

cwd=$(cd $(dirname $0); pwd)
appdir=${cwd}/..

source ${cwd}/.env.sh

pytest ${appdir}/tests/unit --cov rogw/ --ignore-glob=**/fixtures/*
