#!/bin/env python3
# coding: utf8
"""
@File Name  : bin/send_message_to_feishu.py
@Author     : LeeCQ
@Date-Time  : 2023/9/19 14:53

网络管理
"""

import logging
from pathlib import Path

import typer
import yaml

import _base

_base.logging_configurator(
    name="network-manager",
    console_print=True,
    console_level="INFO" if _base.IS_SYSTEMD else "INFO",
    file_level="DEBUG" if _base.IS_SYSTEMD else "INFO",
)

logger = logging.getLogger("host-service.bin.network-manager")
app = typer.Typer()

CONFIG = """
version: 1

wifi:
  - ssid: ziroom302
    password: 4001001111
    
  - ssid: WalmartGuest
    mac: c8:03:ed:33:a0:ad
    
feishu:
  hook_id: 9e40f223-0199-438a-a620-cf01b443dabc
  keyword: null
"""


@app.command()
def auto_connect_wifi(config_file: Path):
    """自动连接Wi-Fi"""
    from network_manger.auto_connect_wifi import AutoConfigWifi, WifiConfig

    config_dict = yaml.safe_load(config_file.read_text(encoding="utf8"))
    logger.info("Loaded Config File Success.")

    config = AutoConfigWifi([WifiConfig(**wifi) for wifi in config_dict["wifi"]])
    status = config.connect()
    logger.info("Connect Wi-Fi: %s", status)

    from send_ip_to_feishu import send_ip

    return send_ip(**config_dict["feishu"])
