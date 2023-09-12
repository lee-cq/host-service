#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File Name  : connect_status.py
@Author     : LeeCQ
@Date-Time  : 2023/9/12 19:40
"""
import asyncio
import subprocess

from client import AClient


def self_tailscale_ip() -> str:
    """获取本机的tailscale ip"""
    return (
        subprocess.run("tailscale ip", capture_output=True)
        .stdout.decode()
        .strip()
        .splitlines(keepends=False)[0]
    )


class ConnectStatus:
    """上报当前节点与其他节点的连接状态"""

    def __init__(self, tsnet, api_key):
        self.client = AClient(tsnet, api_key)
        self.other_nodes: list = []
        self.self_ip = self_tailscale_ip()
        asyncio.create_task(
            self.update_other_nodes(), name=f"update_other_nodes_{tsnet}"
        )

    async def update_other_nodes(self):
        while True:
            self.other_nodes = [
                d for d in await self.client.get_devices() if d.ipv4 != self.self_ip
            ]
            await asyncio.sleep(60)

    async def ping(self, host, timeout=5) -> float:
        """Ping主机并返回延迟时间"""
        proc = await asyncio.create_subprocess_shell(
            f"ping -c 1 -w {timeout* 1000} {host}",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await proc.communicate()
        return proc.returncode == 0

    async def run(self):
        """上报当前节点与其他节点的连接状态"""
        devices = await self.client.get_devices()
        for d in devices:
            print(d.name)
