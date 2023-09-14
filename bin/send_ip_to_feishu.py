#!/bin/env python3
# coding: utf8
"""
@File Name  : bin/send_ip_to_feishu.py
@Author     : LeeCQ
@Date-Time  : 2023/9/14 09:47

将ip推送到飞书
"""
import logging
import re
import socket
import subprocess

import typer

import _base
from tools import getencoding

_base.logging_configurator("send_ip_to_feishu", console_print=True)

logger = logging.getLogger("host-service.bin.send-ip-to-feishu")
app = typer.Typer()

HOSTNAME = socket.gethostname()


def get_ips() -> str:
    """获取本机的所有ip地址"""
    proc = subprocess.run(
        "ip addr | grep inet", shell=True, check=True, stdout=subprocess.PIPE
    )

    return "\n".join(
        re.findall(
            r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", proc.stdout.decode(getencoding())
        )
    )


@app.command()
def send_message(chat_id="oc_935401cad663f0bf845df98b3abd0cf6"):
    from feishu.im_adapter import IMAdapter
    from feishu.client import client

    msg_content = f"设备 {HOSTNAME} 新的IP地址：\n {get_ips()}"

    im = IMAdapter(client)
    resp = im.send_text_message_to_chat(chat_id, msg_content)
    logger.info(resp)


if __name__ == "__main__":
    app()
