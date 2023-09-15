import abc
import asyncio
import logging

from .clash import AClash
from .client_loki import ALokiClient
from .demo.loki import Stream
from .tailscale import Tailscale

logger = logging.getLogger("host-service.grafana.handler")


class InputBase(metaclass=abc.ABCMeta):
    __input_type__: str

    @abc.abstractmethod
    async def to_hardle(self, queue: asyncio.Queue):
        pass


class OutputBase(metaclass=abc.ABCMeta):
    __output_type__: str

    def __init__(self):
        self.queue = asyncio.Queue()

    async def put(self, data):
        await self.queue.put(data)

    @abc.abstractmethod
    async def to_output(self):
        pass


class InputClash(InputBase, AClash):
    __input_type__ = "clash"

    async def to_hardle(self, queue: asyncio.Queue):
        await self.run()
        while True:
            for s in await self.create_streams():
                s: Stream
                await queue.put(s)  # 目前直接写入的Stream对象


class InputPing(InputBase):
    __input_type__ = "ping"

    async def to_hardle(self, queue: asyncio.Queue):
        pass


class InputTailscale(InputBase, Tailscale):
    __input_type__ = "tailscale"

    async def to_hardle(self, queue: asyncio.Queue):
        await self.run()
        while True:
            async for s in self.to_loki():
                s: Stream
                await queue.put(s)


class OutputLoki(OutputBase, ALokiClient):
    __output_type__ = "loki"

    def __init__(
        self, host, user_id, api_key, verify=True, labels: dict = None, **kwargs
    ):
        OutputBase.__init__(self)
        ALokiClient.__init__(
            self, host, user_id, api_key, verify=verify, labels=labels, **kwargs
        )

    async def get_all(self, lens=40) -> list[Stream]:
        """获取所有的ping信息"""
        lens = lens if lens <= self.queue.qsize() else self.queue.qsize()
        return [await self.queue.get() for _ in range(lens)]

    async def to_output(self):
        await self.push(await self.get_all())


class Handler:
    input_class = {
        "clash": InputClash,
        "tailscale": InputTailscale,
    }
    output_class = {
        "loki": OutputLoki,
    }

    def __init__(self):
        self.inputs = []
        self.outputs: list[OutputBase] = []
        self.started_task = {}

        self.queue: asyncio.Queue = asyncio.Queue()

    def register_input(self, type_: str, *args, **kwargs):
        """注册输入"""
        self.inputs.append(self.input_class[type_](*args, **kwargs))

    def register_output(self, type_: str, *args, **kwargs):
        """注册输出"""
        self.outputs.append(self.output_class[type_](*args, **kwargs))

    @property
    def task_names(self):
        return [t.get_name() for t in asyncio.all_tasks()]

    async def push_to_output(self):
        """将输入的数据推送到输出"""
        while True:
            data = await self.queue.get()
            for o in self.outputs:
                await o.put(data)

    async def start(self):
        """启动"""
        for i in self.inputs:
            asyncio.create_task(i.to_hardle(self.queue))

        for o in self.outputs:
            asyncio.create_task(o.to_output())

        asyncio.create_task(self.push_to_output())