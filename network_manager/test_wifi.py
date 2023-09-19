#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File Name  : test_wifi.py
@Author     : LeeCQ
@Date-Time  : 2023/9/17 1:56
"""

from wifi import line_to_list, table_to_dict


def test_table_to_dict():
    tt = """NAME                      UUID                                  TYPE      DEVICE     
Wired connection 1        ba9f5ef4-c1e3-3849-a543-2cbf7c5bdb92  ethernet  eth0       
ziroom302                 8295b4ff-73e8-4ceb-8312-d89d4bef387d  wifi      wlan0      
tailscale0                9cc67ed1-fbc5-4ddb-ad6b-fe43d3bd0175  tun       tailscale0"""
    res = table_to_dict(tt)
    assert res[0]["name"] == "Wired connection 1"
    assert res[1]["uuid"] == "8295b4ff-73e8-4ceb-8312-d89d4bef387d"
    assert res[2]["type"] == "tun"


def test_wifi_status():
    pass