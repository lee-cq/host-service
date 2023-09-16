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


def list_wifi() -> List[Dict[str, Union[str, int]]]:
    """获取Wi-Fi列表"""
    # 1. 扫描Wi-Fi
    _run("nmcli dev wifi rescan")

    # 2. 获取Wi-Fi列表
    res = _run("nmcli dev wifi list")

    # 3. 解析Wi-Fi列表
    wifi_list = []
    for line in res.splitlines()[1:]:
        if not line.strip():
            continue

        # 3.1 解析一行
        wifi = {}
        for i, value in enumerate(re.split(r"\s{2,}", line)):
            if i == 0:
                wifi["SSID"] = value
            elif i == 1:
                wifi["MODE"] = value
            elif i == 2:
                wifi["CHAN"] = int(value)
            elif i == 3:
                wifi["RATE"] = value
            elif i == 4:
                wifi["SIGNAL"] = int(value[:-1])
            elif i == 5:
                wifi["BARS"] = int(value)
            elif i == 6:
                wifi["SECURITY"] = value
            elif i == 7:
                wifi["IN-USE"] = value

        wifi_list.append(wifi)

    return wifi_list


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


def disconnect_wifi() -> bool:
    """断开Wi-Fi"""
    # 1. 断开Wi-Fi
    try:
        _run("nmcli dev disconnect")
    except subprocess.CalledProcessError as e:
        logger.error(f"断开Wi-Fi失败: {e}")
        return False

    # 2. 检查是否断开成功
    res = _run("nmcli dev status")
    for line in res.splitlines()[1:]:
        if not line.strip():
            continue

        if "disconnected" in line:
            return True

    return False


def get_wifi_status() -> Dict[str, Union[str, int]]:
    """获取Wi-Fi状态"""
    # 1. 获取Wi-Fi状态
    res = _run("nmcli dev status")
    for line in res.splitlines()[1:]:
        if not line.strip():
            continue

        # 2. 解析Wi-Fi状态
        wifi_status = {}
        for i, value in enumerate(re.split(r"\s{2,}", line)):
            if i == 0:
                wifi_status["DEVICE"] = value
            elif i == 1:
                wifi_status["TYPE"] = value
            elif i == 2:
                wifi_status["STATE"] = value
            elif i == 3:
                wifi_status["CONNECTION"] = value
            elif i == 4:
                wifi_status["SSID"] = value

        return wifi_status

    return {}
