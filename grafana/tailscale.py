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


from grafana.client_loki import Stream, LokiClient
from health.ping import a_ping_ttl
from tools import getencoding

logger = logging.getLogger("host-service.tailscale.connect_status")


class NotInstallError(Exception):
    """未安装tailscale"""


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

    def __init__(self, **kwargs):
        self.kwargs = kwargs  # 为了兼容老版本的参数接入(新版本不需要任何参数，CLI完成了认证)
        self.self_ip = None
        self.hostname = None
        self.name_prefix = f"tailscale_"
        logger.info("tailscale self IP: %s", self.self_ip)

        self.queue = asyncio.Queue()
        self.active_nodes: dict[str, str] = {}  # ip: hostname

    async def update_ts_status(self):
        """更新Tailscale的状态"""
        try:
            proc = await asyncio.create_subprocess_exec(
                "tailscale",
                "status",
                "--json",
                "--active",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await proc.communicate()
            ts_status = json.loads(stdout.decode(getencoding()))
            ts_status["type"] = "tailscale_status"
            await self.queue.put((time.time_ns(), ts_status))
            logger.debug("Push Tailscale状态. %s", ts_status)

            self.self_ip = ts_status["Self"]["TailscaleIPs"][0]
            self.hostname = ts_status["Self"]["HostName"]
            self.active_nodes = {
                peer["TailscaleIPs"][0]: peer["HostName"]
                for peer in ts_status["Peer"].values()
            }

        except Exception as _e:
            logger.error("tailscale status 执行失败失败: %s, 5秒后重试", _e, exc_info=True)

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
        for node in self.active_nodes.keys():
            name = f"{self.name_prefix}_ping_{node}"
            if name not in [t.get_name() for t in asyncio.all_tasks()]:
                asyncio.create_task(self.ping(node), name=name)
                logger.debug("创建一个ping任务: %s", name)
            await asyncio.sleep(0.1)

    async def to_loki(self) -> AsyncIterable[Stream]:
        """转换为loki格式"""
        logger.info("开始将Tailscale数据转换为Loki格式 ...")
        while True:
            await asyncio.sleep(0.001)
            logger.debug("tailscale to_loki queue size: %d", self.queue.qsize())
            try:
                time_ns, data = await self.queue.get()
                stream = dict(
                    type=data["type"],
                    source=self.hostname,
                )
                if "target" in data:
                    stream.update(target=self.active_nodes.get(data["target"]))

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
                    self.update_ts_status(), name=f"{self.name_prefix}_update_status"
                )
                asyncio.create_task(
                    self.netcheck(), name=f"{self.name_prefix}_netcheck"
                )
                n = 5
                while not self.active_nodes and n:
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

    async def run_with_loki(self, loki_client: LokiClient):
        """使用Loki客户端运行"""

        self.run()
        async for s in self.get_all():
            logger.debug("Queue size: %d", self.queue.qsize())
            if s:
                await loki_client.a_push(s)
