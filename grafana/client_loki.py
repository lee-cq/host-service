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

from httpx import AsyncClient
from pydantic import BaseModel


logger = logging.getLogger("host-service.grafana.client-loki")


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
    def __init__(
        self, host, user_id, api_key, verify=True, labels: dict = None, **kwargs
    ):
        self._labels = dict()
        self.client = AsyncClient(
            base_url=f"https://{host}",
            auth=(str(user_id), api_key),
            verify=verify,
            **kwargs,
        )
        if labels:
            self._labels.update(labels)

    async def push(self, data: list[Stream | dict]) -> int:
        """Push消息, 返回成功推送的消息数量"""
        if not data:
            logger.warning("没有数据 ...")
            return 0
        data = [d for d in data if isinstance(d, (Stream, dict))]
        lens_data = sum(len(_.values) for _ in data)
        if self._labels:
            [s.stream.update(self._labels) for s in data]
        data = {"streams": [i.model_dump() for i in data if isinstance(i, BaseModel)]}
        data = json.dumps(data, ensure_ascii=False)
        url = "/loki/api/v1/push"
        headers = {"Content-Type": "application/json", "Content-Encoding": "gzip"}
        resp = await self.client.post(
            url,
            content=compress(data.encode(), 9),
            headers=headers,
        )
        if resp.status_code == 204:
            logger.debug(
                "Pushed Success: %d, data size: %d, compressed size: %d",
                lens_data,
                len(data),
                len(resp.request.content),
            )
            return lens_data
        logger.warning(
            "loki push Error, code %d, Msg: %s\n%s",
            resp.status_code,
            resp.text,
            data,
        )
        return 0


class ALokiPush(ALokiClient, LokiPushBase):
    def __init__(self, host, user_id, api_key, **kwargs):
        super().__init__(host, user_id, api_key, **kwargs)
        self._labels = {}

    async def push(self, data: list[LogValue]) -> int:
        data = Stream(stream=self._labels, values=data)
        return await super().push([data])
