#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File Name  : model.py
@Author     : LeeCQ
@Date-Time  : 2023/9/12 18:27
"""
import datetime

from pydantic import BaseModel, computed_field


class _Device(BaseModel):
    """https://github.com/tailscale/tailscale/blob/main/api.md#attributes"""

    id: str  # 设备的旧标识符, 可以在{deviceid}的任何地方提供此值, 请注意，尽管“ ID”仍被接受，但“ Nodeid”是首选。
    nodeId: str  # 设备的新标识符, 可以在{deviceid}的任何地方提供此值.
    user: str  # 设备的所有者的用户名.
    hostname: str  # 主机名(字符串)是管理控制台中机器的名称
    clientVersion: str  # clientVersion (string)是Tailscale客户端的版本
    updateAvailable: bool  # updateAvailable (boolean)如果Tailscale客户端版本升级可用，则为true。对于外部设备，此值为空。
    os: str  # OS(字符串)是设备正在运行的操作系统。
    created: str  # 创建（字符串）是将设备添加到尾网上的日期；对于外部设备来说，这是空的。 "2022-12-01T05:23:30Z"
    lastSeen: str  # lastSeen (string)是设备最后一次在Tailscale网络上看到的日期。 "2022-12-01T05:23:30Z"
    keyExpiryDisabled: bool  # keyExpiryDisabled (boolean)如果设备的密钥不会过期，则为true。
    expires: str  # expires (string)是设备的密钥过期日期。
    authorized: bool  # authorized (boolean)如果该设备已被授权加入尾网，则true；否则false。
    isExternal: bool  # isExternal (boolean)如果‘ true’，则表示设备不是 tailnet 的成员，而是在 tailnet 中共享; 如果‘ false’，则表示设备是 tailnet 的成员。
    machineKey: str  # machineKey (string)是设备的机器密钥。内部使用。
    nodeKey: str  # nodeKey（String）主要用于内部使用，是选择操作所需的，例如将节点添加到锁定的尾网上。
    blocksIncomingConnections: str  # 如果不允许该设备接受尾部（包括ping）上的任何连接，则blockSincomingConnections（Boolean）是“ True”的。


class Device(BaseModel):
    """"""

    id: str  # 设备的旧标识符, 可以在{deviceid}的任何地方提供此值, 请注意，尽管“ ID”仍被接受，但“ Nodeid”是首选。
    nodeId: str  # 设备的新标识符, 可以在{deviceid}的任何地方提供此值.
    user: str  # 设备的所有者的用户名.
    updateAvailable: bool  # updateAvailable (boolean)如果Tailscale客户端版本升级可用，则为true。对于外部设备，此值为空。
    os: str  # OS(字符串)是设备正在运行的操作系统。
    authorized: bool  # authorized (boolean)如果该设备已被授权加入尾网，则true；否则false。
    hostname: str  # 主机名(字符串)是管理控制台中机器的名称
    name: str  # name (string)是设备的FQDN名称。
    addresses: list[str]  # addresses (array of strings)是设备的IP地址列表。
    created: datetime.datetime  # 创建（字符串）是将设备添加到尾网上的日期；对于外部设备来说，这是空的。 "2022-12-01T05:23:30Z"
    lastSeen: datetime.datetime  # lastSeen (string)是设备最后一次在Tailscale网络上看到的日期。 "2022-12-01T05:23:30Z"
    expires: datetime.datetime  # expires (string)是设备的密钥过期日期。

    @computed_field()
    def ipv4(self) -> str:
        return [i for i in self.addresses if "." in i][0]

    # __module_config__ = ConfigDict(
    #     json_schema_extra={
    #         "example": {
    #             "addresses": [
    #                 "100.101.154.99",
    #                 "fd7a:115c:a1e0:ab12:4843:cd96:6265:9a63",
    #             ],
    #             "authorized": True,
    #             "blocksIncomingConnections": False,
    #             "clientVersion": "1.46.1-te42e60103-g4cea91365",
    #             "created": "2022-12-25T13:46:57Z",
    #             "expires": "2023-07-31T12:47:38Z",
    #             "hostname": "LeeCQ-PC",
    #             "id": "43063575488320281",
    #             "isExternal": False,
    #             "keyExpiryDisabled": False,
    #             "lastSeen": "2023-08-01T12:47:12Z",
    #             "machineKey": "mkey:21acd934c9d62c1f8a01fb18a162d32cd390e60887fd3f1dac35bdb73b2b7140",
    #             "name": "leecq-pc.tail44b3.ts.net",
    #             "nodeId": "npFUsY4CNTRL",
    #             "nodeKey": "nodekey:8c61bbd6461393d8724667340a4870a6113ece22cd18372b96bbb78c30659a60",
    #             "os": "windows",
    #             "tailnetLockError": "",
    #             "tailnetLockKey": "nlpub:e92c4675578887ae381973e190c1e7fd1906d97a776b893182833853cb349441",
    #             "updateAvailable": True,
    #             "user": "lee-cq@github",
    #         }
    #     }
    # )
