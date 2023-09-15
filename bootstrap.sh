#!/bin/env bash

cd "$(dirname "$0")" || exit

# =================  环境初始化 ==========================
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

md5_saved=$(cat .requirements-installed 2>/dev/null)
md5_file=$(md5sum requirements.txt | awk -F' ' '{print $1}')
if [ "${md5_saved}" != "${md5_file}" ];then
  echo "requirements.txt 已经更新, 重新安装依赖..."
  if [ "$(pip config get global.index-url)" == "" ]; then
    echo "未配置镜像源，设置为： https://pypi.tuna.tsinghua.edu.cn/simple"
    pip config set global.index-url "https://pypi.tuna.tsinghua.edu.cn/simple"
  fi
  pip install -r requirements.txt
  echo "${md5_file}" > .requirements-installed
fi

# ========================= 环境初始化结束 =========================

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
