import abc
import asyncio
import logging
import threading
import time
from queue import Queue as _Queue
from typing import Iterable
from asyncio import Queue as _AQueue

from httpx import AsyncClient, Client

logger = logging.getLogger('host-service.grafana')


class Queue(_Queue):
    """"""

    def get_all(self, lens=20, timeout=1):
        """返回当前队列全部的对象，如果队列为空则等待 {timeout} s后重试"""
        while self.empty():
            time.sleep(timeout)

        if self.qsize() < lens:
            lens = self.qsize()
        return [self.get() for _ in range(lens)]


class AQueue(_AQueue):
    """"""

    async def get_all(self, lens=20, timeout=1) -> list:
        """返回当前队列全部的对象，如果队列为空则等待 {timeout} s后重试"""
        while self.empty():
            await asyncio.sleep(timeout)
        if self.qsize() < lens:
            lens = self.qsize()
        return [self.get() for _ in range(lens)]


class GraphiteBase(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def push(self, content: dict) -> None:
        """向队列中Push一条数据"""

    @abc.abstractmethod
    def pushes(self, contents: Iterable[dict], *args) -> None:
        """向队列中Push多条数据"""


class AGraphiteClient(GraphiteBase):

    def __init__(self, url, user_id, api_key):
        self.client = AsyncClient(
            base_url=url,
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {user_id}:{api_key}'
            },
        )
        self.total = 0
        self.queue = AQueue()
        asyncio.get_running_loop().create_task(self.post())

    async def post(self):
        """从队列中获取数据并推送至Grafana"""
        while True:
            data = await self.queue.get_all()

            resp = await self.client.post('', json=data)
            if resp.status_code // 100 == 2:
                logger.debug("成功推送 %d 条数据", len(data))
                self.total += 1
                continue

            # 推送失败
            logger.warning('推送失败：%s', resp.text)
            await self.pushes(data)

    async def push(self, content: dict) -> None:
        return await self.queue.put(content)

    async def pushes(self, contents: Iterable[dict], *args) -> None:
        for c in contents:
            await self.push(c)
        for a in args:
            if isinstance(a, dict):
                await self.push(a)
            elif isinstance(a, Iterable):
                await self.pushes(a)


class GraphiteClient(GraphiteBase):

    def __init__(self, url, user_id, api_key):
        self.url = url
        self.client = Client(
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {user_id}:{api_key}'
            },
            verify=False
        )
        self.queue = Queue()
        self.total = 0
        self._thead_exit = False
        self.thread = threading.Thread(name='grafana-post',
                                       target=self.post,
                                       daemon=True
                                       )
        self.thread.start()

    def join(self):
        while not self.queue.empty():
            time.sleep(0.5)
        self._thead_exit = True

    def post(self):
        """从队列中获取数据并推送至Grafana"""
        while True:
            if self._thead_exit:
                break
            data = self.queue.get_all()

            resp = self.client.post(self.url, json=data)
            if resp.status_code // 100 == 2:
                logger.debug("成功推送 %d 条数据", len(data))
                self.total += 1
                continue

            # 推送失败
            logger.warning('推送失败：%s', resp.text)
            self.pushes(data)

    def push(self, content: dict) -> None:
        return self.queue.put(content)

    def pushes(self, contents: Iterable[dict], *args) -> None:
        for c in contents:
            self.push(c)
        for a in args:
            if isinstance(a, dict):
                self.push(a)
            elif isinstance(a, Iterable):
                self.pushes(a)
