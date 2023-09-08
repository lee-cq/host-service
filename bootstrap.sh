#!/bin/env bash

cd "$(dirname $0)" || exit

alias python=python3

if [ ! -d venv ];then
  python -m venv venv
fi

source venv/bin/activate

if [ ! -f .requirements-installed ];then
  pip install -r requirements.txt
  pip install -r requirements-dev.txt
  echo > .requirements-installed
fi



action=$1
shift
case $action in
venv )
  exec source venv/bin/activate
  ;;
run )
  cd 'bin/' || exit 1
  exec python "$@"
  ;;
esac