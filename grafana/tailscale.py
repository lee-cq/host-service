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

tz = datetime.timezone(datetime.timedelta(hours=8))


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
        logger.warning("Tailscale API 返回了错误[%d] %s", resp.status_code, resp.text)
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

    EXPIRATION_CONNECT = datetime.timedelta(minutes=120)

    def __init__(self, tsnet, api_key):
        self.client = AClient(tsnet, api_key)
        self.self_ip = self_tailscale_ip()
        self.name_prefix = f"tailscale_{tsnet}"
        logger.info("tailscale self IP: %s", self.self_ip)

        self.queue = asyncio.Queue()
        # self.lock = asyncio.Lock()

        self.other_nodes: list = []
        self.ip_hostname = {}
        # asyncio.create_task(
        #     self.update_other_nodes(), name=f"{self.name_prefix}_nodes_first"
        # )

    async def update_other_nodes(self):
        try:
            ts_nodes = await self.client.get_devices()
            self.ip_hostname = {d.ipv4: d.hostname for d in ts_nodes}
            other_nodes = []
            for d in ts_nodes:
                if d.ipv4 == self.self_ip:
                    logger.debug("self IP %s, continued .", d.ipv4)
                    continue
                if datetime.datetime.now(tz) - d.lastSeen > self.EXPIRATION_CONNECT:
                    logger.debug(
                        "不活跃节点 %s lastSeen=%s, continued .",
                        d.name,
                        d.lastSeen.astimezone(tz).strftime("%Y-%m-%d %H:%M:%S"),
                    )
                    continue
                other_nodes.append(d)
            self.other_nodes = other_nodes
            logger.debug(
                "最新Tailscale节点信息, %s : %s", self.client.tsnet, self.other_nodes
            )
        except Exception as _e:
            logger.warning("更新节点信息是遇见错误： %s", _e, exc_info=True)

    async def netcheck(self):
        """网络检查"""
        try:
            proc = await asyncio.create_subprocess_exec(
                "tailscale",
                "netcheck",
                "--format=json-line",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await proc.communicate()
            netstat = json.loads(stdout.decode(getencoding()))
            netstat["type"] = "tailscale_netcheck"
            logger.debug("Push 网络检查结果. %s", netstat)
            await self.queue.put((time.time_ns(), netstat))
        except Exception as _e:
            logger.error("网络检查失败: %s, 5秒后重试", _e, exc_info=True)

    async def ping(self, host, timeout=5):
        """Ping主机并返回延迟时间"""
        async for t in a_ping_ttl(host, timeout):
            logger.debug("Push Ping 结果：%s, %s", host, t)
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
        for node in self.other_nodes:
            name = f"{self.name_prefix}_ping_{node.ipv4}"
            if name not in [t.get_name() for t in asyncio.all_tasks()]:
                asyncio.create_task(self.ping(node.ipv4), name=name)
                logger.debug("创建一个ping任务: %s", name)
            await asyncio.sleep(0.1)

    async def to_loki(self) -> AsyncIterable[Stream]:
        """转换为loki格式"""
        logger.info("开始将Tailscale数据转换为Loki格式 ...")
        while True:
            await asyncio.sleep(0)
            logger.debug("tailscale to_loki queue size: %d", self.queue.qsize())
            try:
                time_ns, data = await self.queue.get()
                stream = dict(
                    type=data["type"],
                    source=self.ip_hostname.get(self.self_ip),
                )
                if "target" in data:
                    stream.update(target=self.ip_hostname.get(data["target"]))

                value = json.dumps(data["ttl"]) if "ttl" in data else json.dumps(data)
                logger.debug("tailscale to_loki stream=%s, data=%s", stream, value)
                yield Stream(stream=stream, values=[(str(time_ns), value)])
            except Exception as _e:
                logger.warning("tailscale to_loki error: %s", _e, exc_info=True)

    def run(self):
        """每分钟创建一个ping任务"""

        async def _run():
            while True:
                asyncio.create_task(
                    self.update_other_nodes(), name=f"{self.name_prefix}_update_nodes"
                )
                asyncio.create_task(
                    self.netcheck(), name=f"{self.name_prefix}_netcheck"
                )
                n = 5
                while not self.other_nodes and n:
                    n -= 1
                    await asyncio.sleep(1)
                asyncio.create_task(
                    self.create_pings(), name=f"{self.name_prefix}_pings"
                )
                await asyncio.sleep(60)

        asyncio.create_task(_run(), name=f"{self.name_prefix}_run")
        logger.info("tailscale run() started success.")

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

        self.run()
        async for s in self.get_all():
            logger.debug("Queue size: %d", self.queue.qsize())
            if s:
                await loki_client.push(s)
