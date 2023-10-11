import abc
import asyncio
import logging

from tools import timestamp_s, human_timedelta
from .clash import AClash
from .client_loki import LokiBufferPush
from .client_loki import Stream
from .tailscale import Tailscale

logger = logging.getLogger("host-service.grafana.handler")


class InputBase(metaclass=abc.ABCMeta):
    __input_type__: str

    @abc.abstractmethod
    async def to_handle(self, queue: asyncio.Queue):
        pass


class InputClash(InputBase, AClash):
    __input_type__ = "clash"

    async def to_handle(self, queue: asyncio.Queue):
        logger.info("开始加载 AClash 内容 ...")
        await self.run()
        logger.info("AClash加载成功, 准备向queue推送数据 ...")
        while True:
            await asyncio.sleep(1)
            for s in await self.create_streams():
                s: Stream
                await queue.put(s)  # 目前直接写入的Stream对象
                logger.debug("AClash %s -> Handler : %s", self.host, s)


class InputPing(InputBase):
    __input_type__ = "ping"

    async def to_handle(self, queue: asyncio.Queue):
        pass


class InputTailscale(InputBase, Tailscale):
    __input_type__ = "tailscale"

    async def to_handle(self, queue: asyncio.Queue):
        logger.info("初始化 Tailscale 内容 ...")
        self.run()
        await asyncio.sleep(1)
        logger.info("开始加载 Tailscale 内容 ...")
        async for s in self.to_loki():
            s: Stream
            await queue.put(s)
            logger.debug("Tailscale -> Handler : %s", s)


class OutputLoki(LokiBufferPush):
    __output_type__ = "loki"

    def __init__(
        self, host, user_id, api_key, verify=True, labels: dict = None, **kwargs
    ):
        LokiBufferPush.__init__(
            self,
            40,
            host,
            user_id,
            api_key,
            flush_timeout=5,
            verify=verify,
            labels=labels,
            **kwargs,
        )
        self.total_push = 0


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
        self.outputs: list[OutputLoki] = []
        self.started_task = {}

        self.total_stream = 0

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
            self.total_stream += 1
            for o in self.outputs:
                await o.put(data)

    async def start(self):
        """启动"""

        asyncio.create_task(self.push_to_output())
        logger.info("创建数据分发task成功 。")

        asyncio.current_task().set_name("Main")
        logger.info("启动看门狗")
        start_time, _stream = timestamp_s(), 0
        while True:
            for i in self.inputs:
                i: InputBase
                name = f"input_{i.__input_type__}_{i.__hash__()}"
                if name in self.task_names:
                    continue
                asyncio.create_task(
                    i.to_handle(self.queue),
                    name=name,
                )
                logger.info(f"创建输入 task %s", i.__input_type__)

            await asyncio.sleep(60)
            logger.info(
                "持续运行时间: %s, 转发数据: %d, 最近一分钟转发数据: %d, 注册的队列大小: %s",
                human_timedelta(timestamp_s() - start_time),
                self.total_stream,
                self.total_stream - _stream,
                ", ".join(f"{k}: {v}" for k, v in self.queue_size().items()),
            )
            _stream = self.total_stream
            logger.debug("当前所有的task: %s", self.task_names)

    def queue_size(self) -> dict:
        rest = {self.__class__.__name__: self.queue.qsize()}
        for i in self.inputs:
            if hasattr(i, "queue"):
                rest[i.__input_type__] = i.queue.qsize()
        for o in self.outputs:
            if hasattr(o, "queue"):
                rest[o.__output_type__] = o.queue.qsize()
        return rest
