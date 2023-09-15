#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File Name  : tailscale.py
@Author     : LeeCQ
@Date-Time  : 2023/9/12 19:40
"""
import asyncio
import datetime
import json
import logging
import subprocess
import time
from typing import AsyncIterable

from httpx import AsyncClient, BasicAuth
from pydantic import BaseModel, computed_field

from grafana.client_loki import Stream, ALokiClient
from health.ping import a_ping_ttl
from tools import getencoding

logger = logging.getLogger("host-service.tailscale.connect_status")


class NotInstallError(Exception):
    """未安装tailscale"""


class Device(BaseModel):
    """https://github.com/tailscale/tailscale/blob/main/api.md#attributes"""

    id: str  # 设备的旧标识符, 可以在{deviceid}的任何地方提供此值, 请注意，尽管“ ID”仍被接受，但“ NodeId”是首选。
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


class AClient(AsyncClient):
    """Tailscale API Client"""

    def __init__(self, tsnet, api_key, *args, **kwargs):
        super().__init__(*args, base_url="https://api.tailscale.com/api/v2", **kwargs)

        self.headers.update({"Content-Type": "application/json"})
        self.auth = BasicAuth(api_key, "")
        self.tsnet = tsnet

    async def get_devices(self) -> list[Device]:
        """获取设备列表"""
        resp = await self.get(f"tailnet/{self.tsnet}/devices")
        if resp.status_code == 200:
            return [Device(**i) for i in resp.json()["devices"]]
        return []

    async def test_get_devices(self):
        """获取设备列表"""
        devices = await self.get_devices()
        for d in devices:
            print(d)


def self_tailscale_ip() -> str:
    """获取本机的tailscale ip"""
    try:
        return (
            subprocess.run(["tailscale", "ip"], capture_output=True, check=True)
            .stdout.decode()
            .strip()
            .splitlines(keepends=False)[0]
        )
    except subprocess.CalledProcessError:
        raise NotInstallError("未安装tailscale")


class Tailscale:
    """上报当前节点与其他节点的连接状态"""

    def __init__(self, tsnet, api_key):
        self.client = AClient(tsnet, api_key)
        self.other_nodes: list = []
        self.ip_hostname = {}
        self.self_ip = self_tailscale_ip()

        self.queue = asyncio.Queue()
        self.lock = asyncio.Lock()

    async def update_other_nodes(self):
        while True:
            ts_nodes = await self.client.get_devices()
            self.ip_hostname = {d.ipv4: d.hostname for d in ts_nodes}
            self.other_nodes = [d for d in ts_nodes if d.ipv4 != self.self_ip]
            await asyncio.sleep(60)

    async def netcheck(self, name):
        """网络检查"""
        try:
            proc = await asyncio.create_subprocess_exec(
                "tailscale",
                "netcheck",
                "--format json-line",
                stdout=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await proc.communicate()
            netstat = json.loads(stdout.decode(getencoding()))
            netstat["type"] = "tailscale_netcheck"
            await self.queue.put((time.time_ns(), netstat))
        except Exception as _e:
            logger.error("网络检查失败: %s, 5秒后重试", _e, exc_info=True)
        await asyncio.sleep(5)
        asyncio.create_task(self.netcheck(name), name=name)

    async def ping(self, host, timeout=5):
        """Ping主机并返回延迟时间"""
        async for t in a_ping_ttl(host, timeout):
            await self.queue.put(
                (
                    time.time_ns(),
                    {
                        "type": "tailscale_ping",
                        "source": self.self_ip,
                        "target": host,
                        "ttl": t,
                    },
                )
            )

    async def create_pings(self):
        """上报当前节点与其他节点的连接状态"""
        while True:
            for node in self.other_nodes:
                name = f"tailscale_ping_{node.ipv4}"
                if name not in [t.get_name() for t in asyncio.all_tasks()]:
                    asyncio.create_task(self.ping(node.ipv4), name=name)
            await asyncio.sleep(60)

    async def to_loki(self) -> AsyncIterable[Stream]:
        """转换为loki格式"""
        while True:
            time_ns, data = await self.queue.get()
            if self.queue.empty():
                await asyncio.sleep(1)
                yield None
            stream = dict(
                type=data["type"],
                source=self.self_ip,
            )
            if "target" in data:
                stream.update(target=self.ip_hostname.get(data["target"]))

            value = json.dumps(data["ttl"]) if "ttl" in data else json.dumps(data)

            yield Stream(stream=stream, values=[(str(time_ns), value)])

    def run(self):
        asyncio.create_task(
            self.update_other_nodes(),
            name=f"tailscale_update_other_nodes_{self.client.tsnet}",
        )
        asyncio.create_task(
            self.netcheck("tailscale_netcheck"), name="tailscale_netcheck"
        )
        asyncio.create_task(self.create_pings(), name="tailscale_create_pings")

    async def get_all(self, lens=20) -> AsyncIterable[list]:
        """获取所有的ping信息"""
        rest, _len = [], 0
        async for s in self.to_loki():
            _len += 1

            if s is not None:
                rest.append(s)

            if _len >= lens:
                yield rest
                rest, _len = [], 0

    async def run_with_loki(self, loki_client: ALokiClient):
        """使用Loki客户端运行"""
        with self.lock:
            self.run()
            async for s in self.get_all():
                logger.debug("Queue size: %d", self.queue.qsize())
                if s:
                    await loki_client.push(s)
