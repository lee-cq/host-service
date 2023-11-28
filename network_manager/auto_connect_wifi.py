#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File Name  : network_manager/auto_config_wifi.py
@Author     : LeeCQ
@Date-Time  : 2023/9/16 19:36

Linux Wi-Fi 操作
"""
import logging

from pydantic import BaseModel, Field

from .wifi import (
    list_wifi,
    connect_wifi,
    disconnect_wifi,
    get_wifi_status,
    update_device_mac,
    WifiInfo
)

logger = logging.getLogger("host-service.network_manger.auto_connect_wifi")


class WifiConfig(BaseModel):
    """Wi-Fi配置"""

    ssid: str
    password: str = Field(None, strict=False)
    mac: str = Field(None, strict=False)


class AutoConfigWifi:
    """自动配置WIFI"""

    def __init__(self, configs: list[WifiConfig]):
        self.configs = configs
        self.used_config, self.used_wifi = self.__used_config()
        logger.debug("Config Inited ...")

    def __used_config(self) -> tuple[WifiConfig, WifiInfo]:
        """获取当前使用的Wi-Fi"""
        wifi_lists = {i.ssid: i for i in list_wifi()}
        for wc in self.configs:
            wc: WifiConfig
            if wc.ssid in wifi_lists:
                logger.info("返回使用的ID：\nwc:: %s\nwifi_lists[wc.ssid]:: %s", wc, wifi_lists[wc.ssid])
                return wc, wifi_lists[wc.ssid]
        
        logger.warning(
            "目前Wifi列表中没有找到配置能被配置。\n"
            "被配置的SSID: %s\n"
            "找到的SSID: %s",
            "  ".join([i.ssid for i in self.configs]),
            "  ".join(wifi_lists.keys()),
                       )
        exit(0)

    def connect(self) -> bool:
        """连接Wi-Fi"""
        logger.info("准备连接到 SSID %s ...", self.used_config.ssid)
        
        if self.used_wifi.in_use == "*":
            logger.info("已经连接到 SSID: %s, 退出 ...", self.used_config.ssid)
            return True
        
        if self.used_config.mac is not None:
            logger.info("找到MAC地址, 准备更新 -> %s", self.used_config.mac)
            if update_device_mac("wlan0", self.used_config.mac):
                logger.info("已经更新MAC地址。")
        
        logger.info("连接到Wi-Fi： ssid=%s, password=%s", self.used_config.ssid, self.used_config.password)
        return connect_wifi(self.used_config.ssid, self.used_config.password)

    def run(self):
        return self.connect()


if __name__ == "__main__":
    wifi_configs = [
        WifiConfig(ssid="WalmartGuest", mac="c8:03:ed:33:a0:ad"),
        WifiConfig(ssid="ziroom302", password="4001001111"),
    ]

    au = AutoConfigWifi(wifi_configs)
    au.connect()
