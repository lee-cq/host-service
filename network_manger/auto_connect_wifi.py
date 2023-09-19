#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File Name  : au
@Author     : LeeCQ
@Date-Time  : 2023/9/16 19:36

Linux Wi-Fi 操作
"""
import logging

from pydantic import BaseModel

from .wifi import (
    list_wifi,
    connect_wifi,
    disconnect_wifi,
    get_wifi_status,
    update_device_mac,
)

logger = logging.getLogger("host-service.network_manger.auto_connect_wifi")


class WifiConfig(BaseModel):
    """Wi-Fi配置"""

    ssid: str
    password: str = None
    mac: str = None


class AutoConfigWifi:
    """自动配置WIFI"""

    def __init__(self, configs: list[WifiConfig]):
        self.configs = configs
        self.used_config = self.used_ssid()

    def used_ssid(self) -> WifiConfig:
        """获取当前使用的Wi-Fi"""
        now_ssids = [i["SSID"] for i in list_wifi()]
        for i in self.configs:
            if i.ssid in now_ssids:
                return i

    def connect(self) -> bool:
        """连接Wi-Fi"""

        if self.used_config.ssid == get_wifi_status().connection:
            return True
        if self.used_config.mac is not None:
            if update_device_mac("wlan0", self.used_config.mac):
                return False
        return connect_wifi(self.configs[0].ssid, self.configs[0].password)

    def run(self):
        return self.connect()


if __name__ == "__main__":
    wifi_configs = [
        WifiConfig(ssid="WalmartGuest", mac="c8:03:ed:33:a0:ad"),
        WifiConfig(ssid="ziroom302", password="4001001111"),
    ]

    au = AutoConfigWifi(wifi_configs)
    au.connect()
