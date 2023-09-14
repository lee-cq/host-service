#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File Name  : create_service.py
@Author     : LeeCQ
@Date-Time  : 2023/9/12 14:29

创建服务

"""

import os
import logging
from pathlib import Path

import typer


app = typer.Typer()
logger = logging.getLogger("host-service.bin.create-service")

WORKDIR = Path(__file__).parent.parent.absolute()

if os.name == "nt":
    raise OSError("不支持Windows系统")


def join_exec_start(name: str, *args, **kwargs):
    """拼接ExecStart字符串"""
    exec_start = f"{WORKDIR.absolute().joinpath('bootstrap.sh')} run {name} "
    for k, v in kwargs.items():
        exec_start += f"--{k.replace('_', '-')} {v} "

    return exec_start + " " + " ".join(args)


def join_service(name, exec_start):
    """拼接Service字符串"""
    return (
        f"\n[Unit]"
        f"\nDescription={name}"
        f"\nAfter=network.target"
        f"\n"
        f"\n[Service]"
        f"\nType=simple"
        f"\nWorkingDirectory={WORKDIR}"
        f"\nExecStart={exec_start}"
        f"\nRestart=on-failure"
        f"\nRestartSec=5s"
        f"\n"
        f"\n[Install]"
        f"\nWantedBy=default.target"
        f"\n"
    )


def create_service_file(name, service):
    """创建Service文件"""
    if name.endswith(".py"):
        name = name[:-3]

    name = name.replace("_", "-")
    user_service_dir = Path.home().joinpath(".config", "systemd", "user")
    user_service_dir.mkdir(parents=True, exist_ok=True)

    service_file = user_service_dir.joinpath(f"{name}.service")
    if service_file.exists():
        logger.info(f"Service file already exists: {service_file}")
        if input(f"{service_file}已经存在, 是否覆盖? [y/n]: ").lower() != "y":
            logger.info("已取消")
            return
    service_file.write_text(service, encoding="utf8")
    logger.info(f"Created service file: {service_file}")


def _create_service(name, *args, **kwargs):
    """"""
    logger.info(f"当前工作目录: {WORKDIR}")

    exec_start = join_exec_start(name, *args, **kwargs)
    logger.info(f"exec_start: {exec_start}")
    service = join_service(WORKDIR.joinpath("bin", name), exec_start)
    logger.debug(f"service String: >>>\n%s\n<<<", service)
    if name.endswith(".py"):
        name = name[:-3]

    name = name.replace("_", "-")
    create_service_file(name, service)
    os.system("systemctl --user daemon-reload")

    logger.info("服务创建成功, 请执行以下命令:\n")
    logger.info(f"启动服务: systemctl --user start {name}")
    logger.info(f"设置开机自启: systemctl --user enable {name}")
    logger.info(f"查看服务状态: systemctl --user status {name}")
    logger.info(f"停止服务: systemctl --user stop {name}")


@app.command()
def send_ip_to_feishu(
    chat_id: str = "oc_935401cad663f0bf845df98b3abd0cf6",
):
    """"""
    name = "send_ip_to_feishu.py"

    return _create_service(name, chat_id=chat_id)


@app.command()
def ping_info(
    host: str,
    timeout: int = 60,
    chat_id: str = "oc_935401cad663f0bf845df98b3abd0cf6",
):
    """"""
    name = "ping_info.py"

    return _create_service(name, host, timeout, chat_id)


@app.command()
def clash_to_loki(
    clash_host: str = None,
    clash_token: str = None,
    loki_host: str = None,
    loki_user_id: str = None,
    loki_api_key: str = None,
):
    """"""
    # 获取当前用户 & 组
    name = "clash_to_loki.py"

    if not (clash_host and clash_token and loki_host and loki_user_id and loki_api_key):
        raise KeyError("缺少参数, 请使用 --help 查看帮助")

    return _create_service(
        name,
        clash_host=clash_host,
        clash_token=clash_token,
        loki_host=loki_host,
        loki_user_id=loki_user_id,
        loki_api_key=loki_api_key,
    )


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s - %(message)s"
    )
    app()
