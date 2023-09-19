#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File Name  : wifi.py
@Author     : LeeCQ
@Date-Time  : 2023/9/16 19:36

Linux Wi-Fi 操作

使用同步操作
"""

import os
import re
import subprocess
import logging
from typing import List, Dict, Union

from pydantic import BaseModel, Field

from tools import getencoding

logger = logging.getLogger("host-service.network_manger.wifi")

if os.name == "nt":
    raise OSError("不支持Windows系统")


def _run(cmd: str) -> str:
    """执行命令"""
    logger.debug(f"执行命令: {cmd}")
    return subprocess.check_output(
        cmd, shell=True, encoding=getencoding(), stderr=subprocess.STDOUT
    )


def line_to_list(line: str) -> List[str]:
    """将一行转换为列表"""
    return re.split(r"\s{2,}", line)


def table_to_dict(table: str) -> List[Dict[str, str]]:
    """将表格转换为字典"""
    res = []
    title, content = table.split("\n", maxsplit=1)
    title: list = line_to_list(table.splitlines()[0])
    title = [t.lower() for t in title]
    for line in content.splitlines():
        if not line.strip():
            continue

        line = line_to_list(line)
        res.append(dict(zip(title, line)))
    return res


class WifiList(BaseModel):
    in_use: str | None = Field(None, alias="in-use")
    bssid: str
    ssid: str
    mode: str
    chan: int
    rate: str
    signal: int
    bars: str
    security: str


def list_wifi() -> List[WifiList]:
    """获取Wi-Fi列表"""
    # 1. 扫描Wi-Fi
    _run("nmcli dev wifi rescan")

    # 2. 获取Wi-Fi列表
    res = _run("nmcli dev wifi list")

    # 3. 解析Wi-Fi列表
    return [WifiList(**l) for l in table_to_dict(res)]


class DeviceStatus(BaseModel):
    device: str = "wlan0"
    type: str = "wifi"
    status: str
    connection: str


def device_status() -> List[DeviceStatus]:
    """获取Wi-Fi状态"""
    # 1. 获取Wi-Fi状态
    res = _run("nmcli dev status")
    return [DeviceStatus(**d) for d in table_to_dict(res)]


def get_wifi_status() -> DeviceStatus:
    for d in device_status():
        if d.device == "wifi":
            return d


def connect_wifi(ssid: str, password: str) -> bool:
    """连接Wi-Fi"""
    # 1. 连接Wi-Fi
    try:
        _run(f"nmcli dev wifi connect {ssid} password {password}")
    except subprocess.CalledProcessError as e:
        logger.error(f"连接Wi-Fi失败: {e}")
        return False

    # 2. 检查是否连接成功
    res = _run("nmcli dev status")
    for line in res.splitlines()[1:]:
        if not line.strip():
            continue

        if ssid in line:
            return True

    return False


def disconnect_wifi(device) -> bool:
    """断开Wi-Fi"""
    # 1. 断开Wi-Fi
    try:
        _run(f"nmcli dev  disconnect {device}")
    except subprocess.CalledProcessError as e:
        logger.error(f"断开Wi-Fi失败: {e}")
        return False

    # 2. 检查是否断开成功
    for d in device_status():
        if d.device == device:
            if d.connection == "disconnected":
                return True
            break
    return False


def update_device_mac(device, mac) -> bool:
    """更改设备的MAC地址"""
    # 1. 检查是否存在该设备
    res = [d.device for d in device_status()]
    if device not in res:
        logger.error(f"不存在该设备: {device}")
        return False

    # 2. 更改设备的MAC地址
    try:
        _run(f"sudo ip link set dev {device} down")
        _run(f"sudo ip link set dev {device} address {mac}")
        _run(f"sudo ip link set dev {device} up")
    except subprocess.CalledProcessError as e:
        logger.error(f"更改设备的MAC地址失败: {e}")
        return False

    logger.info(f"更改设备的MAC地址成功: {device} {mac}")
    return mac in _run(f"ip address show {device}")
