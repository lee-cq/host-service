#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File Name  : service.py
@Author     : LeeCQ
@Date-Time  : 2023/9/12 14:29

创建服务  创建系统级服务，需要root权限
创建的服务是对系统服务的支持应该随系统启动。

"""

import os
import logging
from pathlib import Path

import typer
from pydantic import BaseModel


logger = logging.getLogger("host-service.bin.create-service")

WORKDIR = Path(__file__).parent.parent.absolute()
# SERVICE_DIR_USER = Path.home().joinpath(".config", "systemd", "user")
SERVICE_DIR_SYSTEM = Path("/usr/lib/systemd/system")
SERVICE_DIR = SERVICE_DIR_SYSTEM

USER_NAME = os.environ.get("USER")


app = typer.Typer(name="service")
app_create = typer.Typer()
app.add_typer(app_create, name="create", help="创建service")


class AppConfig(BaseModel):
    restart: str = "on-failure"
    restart_sec: int = 5
    user: str = USER_NAME
    group: str | None = None
    debug: bool = False


APP_CONFIG = AppConfig()


@app.callback()
def callback(
    restart: str = "on-failure",
    restart_sec: int = 5,
    user: str = USER_NAME,
    group: str = None,
    debug: bool = False,
):
    """创建服务  创建系统级服务，需要root权限
    创建的服务是对系统服务的支持应该随系统启动。
    """
    APP_CONFIG.restart = restart.lower()
    APP_CONFIG.restart_sec = restart_sec
    APP_CONFIG.user = user
    APP_CONFIG.group = group
    APP_CONFIG.debug = False

    if os.name == "nt" and not debug:
        raise OSError("不支持Windows系统")


def join_exec_start(name: str, *args, **kwargs):
    """拼接ExecStart字符串"""
    exec_start = f"{WORKDIR.absolute().joinpath('bootstrap.sh')} run {name} "
    for k, v in kwargs.items():
        exec_start += f"--{k.replace('_', '-')} {v} "

    return exec_start + " " + " ".join(str(_) for _ in args)


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
        f"\nRestart={APP_CONFIG.restart}"
        f"\nRestartSec={APP_CONFIG.restart_sec}s"
        f"\n"
        f"\n[Install]"
        f"\nWantedBy=multi-user.target"
        f"\n"
    )


def create_service_file(name, service):
    """创建Service文件"""
    if name.endswith(".py"):
        name = name[:-3]

    name = name.replace("_", "-")

    SERVICE_DIR.mkdir(parents=True, exist_ok=True)
    service_file = SERVICE_DIR.joinpath(f"{name}.service")
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


@app_create.command(name="send-ip-to-feishu")
def send_ip_to_feishu(
    hook_id: str = "9e40f223-0199-438a-a620-cf01b443dabc",
    keyword: str = None,
    secret: str = None,
):
    """"""
    name = "send_ip_to_feishu.py"

    return _create_service(name, hook_id=hook_id, keyword=keyword, secret=secret)


@app_create.command(name="ping-info")
def ping_info(
    host: str,
    timeout: int = 60,
    chat_id: str = "oc_935401cad663f0bf845df98b3abd0cf6",
):
    """"""
    name = "ping_info.py"

    return _create_service(name, host, timeout, chat_id)


@app_create.command(name="clash-to-loki")
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


@app_create.command(name="to-loki")
def to_loki(file: Path):
    """"""
    name = "to_loki.py"
    if not file.exists():
        raise FileNotFoundError(f"文件不存在: {file}")
    file = file.absolute()

    return _create_service(name, file)


@app.command()
def start(service_name: str):
    """启动一个service"""


@app.command(name="stop")
def stop(service_name: str):
    """停止一个service"""
    pass


@app.command(name="list")
def list_(all: bool = False):
    """列出已经安装的service"""
    commands = [c.name + ".service" for c in app_create.registered_commands]
    if all:
        print("全部支持的service:", commands)
        return commands
    commands = [c for c in commands if SERVICE_DIR.joinpath(c).exists()]
    print("已经安装的service:", commands)
    return commands


@app.command()
def status(service_name: str):
    """查看service状态"""
    os.system("systemctl --user status " + service_name)


@app.command()
def delete(service_name: str):
    """删除一个service"""
    os.system("systemctl --user stop " + service_name)
    os.system("systemctl --user disable " + service_name)
    os.system("rm -rf " + str(SERVICE_DIR.joinpath(service_name + ".service")))


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s - %(message)s"
    )
    # app_create()
    app()
