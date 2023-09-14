#!/bin/env bash

cd "$(dirname $0)" || exit


_py="$(which python3.11)"
PYTHON=${PYTHON_EXE:-${_py}}
if [ "${PYTHON}x" == "x" ];then
  echo "目前需要安装python3.11或者如果不在PATH中，使用 PYTHON_EXE 环境变量指定. " >&2
  exit 1
fi

if [ ! -d venv ];then
  echo "创建虚拟环境 ..."
  $PYTHON -m venv venv
  rm -f .requirements-installed
fi

source venv/bin/activate

which python3
python3 -V


if [ ! -f .requirements-installed ];then
  if [ "$(pip config get global.index-url)" == "" ]; then
    echo "设置镜像源： https://pypi.tuna.tsinghua.edu.cn/simple"
    pip config set global.index-url "https://pypi.tuna.tsinghua.edu.cn/simple"
  fi
  echo "安装依赖 ..."
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
