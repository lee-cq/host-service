#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File Name  : client.py
@Author     : LeeCQ
@Date-Time  : 2023/9/12 18:53
"""
import asyncio

from httpx import AsyncClient, BasicAuth

from model import Device


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


if __name__ == "__main__":
    asyncio.run(
        AClient(
            "lee-cq.github", "tskey-api-k6FM3Z2CNTRL-1cPt87WfV4bQoC7zzTB3yaJBUkFCWeV4"
        ).test_get_devices()
    )
