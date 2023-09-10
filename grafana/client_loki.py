#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@File Name  : client_loki.py
@Author     : LeeCQ
@Date-Time  : 2023/9/10 14:20
"""

import abc
import json
import logging
from gzip import compress
from collections import namedtuple

from httpx import AsyncClient, Client
from pydantic import BaseModel


logger = logging.getLogger("host-service.grafana.loki")


LogValue = namedtuple("log_value", ["time_ns", "line"])


class Stream(BaseModel):
    stream: dict
    values: list[LogValue]


class LokiClientBase(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def push(self, data: list[Stream]):
        """"""


class LokiPushBase(metaclass=abc.ABCMeta):
    def __init__(self):
        self._labels = {}

    def set_label(self, k: str, v: str) -> None:
        self._labels[k] = v

    def set_labels(self, labels: dict) -> None:
        self._labels.update(labels)


class ALokiClient(LokiClientBase):
    def __init__(self, host, user_id, api_key, verify=True, **kwargs):
        self.client = AsyncClient(
            base_url=f"https://{host}",
            auth=(user_id, api_key),
            # headers={'Authorization': f'Bearer {user_id}:{api_key}'},
            verify=verify,
            **kwargs,
        )

    async def push(self, data: list[Stream | dict]) -> int:
        """Push消息, 返回成功推送的消息数量"""
        lens_data = sum(len(_.values) for _ in data)
        data = {"streams": [i.model_dump() for i in data if isinstance(i, BaseModel)]}
        url = "/loki/api/v1/push"
        headers = {"Content-Type": "application/json", "Content-Encoding": "gzip"}
        data = compress(json.dumps(data).encode(), 9)  # 压缩数据
        resp = await self.client.post(url, content=data, headers=headers)
        if resp.status_code == 204:
            logger.debug("Pushed Success: %d, data size: %d", lens_data, len(data))
            return lens_data
        logger.warning("Loki push Error, code: %d.", resp.status_code)
        logger.debug("loki push Error, code %d, Msg: %s", resp.status_code, resp.text)
        return 0


class ALokiPush(ALokiClient, LokiPushBase):
    def __init__(self, host, user_id, api_key, **kwargs):
        super().__init__(host, user_id, api_key, **kwargs)
        self._labels = {}

    async def push(self, data: list[LogValue]) -> int:
        data = Stream(stream=self._labels, values=data)
        return await super().push([data])


class LokiClient(LokiClientBase):
    def __init__(self, host, user_id, api_key, verify=True, **kwargs):
        self.client = Client(
            base_url=f"https://{host}",
            auth=(user_id, api_key),
            # headers={'Authorization': f'Bearer {user_id}:{api_key}'},
            verify=verify,
            **kwargs,
        )

    def push(self, data: list[Stream]) -> int:
        """Push消息, 返回成功推送的消息数量"""
        lens_data = sum(len(_.values) for _ in data)
        data = {"streams": [i.model_dump() for i in data if isinstance(i, BaseModel)]}
        url = "/loki/api/v1/push"
        resp = self.client.post(
            url,
            json=data,
        )
        if resp.status_code == 204:
            return lens_data
        logger.warning("Loki push Error, code: %d.", resp.status_code)
        logger.debug("loki push Error, code %d, Msg: %s", resp.status_code, resp.text)
        return 0

    def query(self, query: str, limit: int = 100) -> list[dict]:
        """查询日志, 返回查询结果"""
        url = "/loki/api/v1/query_range"
        params = {
            "query": query,
            "limit": limit,
        }
        resp = self.client.get(url, params=params)
        if resp.status_code != 200:
            logger.warning("Loki query Error, code: %d.", resp.status_code)
            logger.debug(
                "loki query Error, code %d, Msg: %s", resp.status_code, resp.text
            )
            return []
        return resp.json().get("data", {}).get("result", [])

    def query_range(
        self, query: str, start: int, end: int, limit: int = 100
    ) -> list[dict]:
        """查询日志, 返回查询结果"""
        url = "/loki/api/v1/query_range"
        params = {
            "query": query,
            "start": start,
            "end": end,
            "limit": limit,
        }
        resp = self.client.get(url, params=params)
        if resp.status_code != 200:
            logger.warning("Loki query Error, code: %d.", resp.status_code)
            logger.debug(
                "loki query Error, code %d, Msg: %s", resp.status_code, resp.text
            )
            return []
        return resp.json().get("data", {}).get("result", [])


class LokiPush(LokiClient, LokiPushBase):
    def __init__(self, host, user_id, api_key, **kwargs):
        super().__init__(host, user_id, api_key, **kwargs)

        self._labels = {}

    def push(self, data: list[LogValue]) -> int:
        data = Stream(stream=self._labels, values=data)
        return super().push([data])
