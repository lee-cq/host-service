import asyncio
import json
import logging.handlers
import os
import threading

from grafana.client_loki import LokiClient
from grafana.client_loki import Stream


class LokiHandler(logging.Handler):
    def __init__(self, flush_level, capacity, host, user_id, api_key, **kwargs):
        super().__init__()
        self.flushLevel: int = (
            flush_level
            if isinstance(flush_level, int)
            else logging.getLevelName(flush_level.upper())
        )
        self.capacity = capacity
        self.loki_client = LokiClient(
            host,
            user_id,
            api_key,
            **kwargs,
        )
        self.buffer = asyncio.Queue()
        self.thread_pool = None

    def shouldFlush(self, record):
        """检查Buffer是否满了或者日志级别达到flushLevel"""
        return record.levelno >= self.flushLevel or self.buffer.qsize() >= self.capacity

    def get_buffer(self) -> list:
        return [self.buffer.get_nowait() for _ in range(self.buffer.qsize())]

    def flush(self) -> None:
        """将缓存的日志推送到loki"""
        if asyncio.get_event_loop().is_running():
            asyncio.create_task(
                self.loki_client.a_push(self.get_buffer())
            )  # TODO 考虑推送失败的情况
        else:
            threading.Thread(
                target=self.loki_client.push, args=(self.get_buffer(),), daemon=False
            ).start()

    def close(self) -> None:
        """关闭loki client"""
        self.flush()

    def emit(self, record):
        # 处理record, 转换为Stream
        stream = {
            "app": "python-tailscale",
            "name": record.name,
            "reportNode": os.getenv("HOSTNAME", "unknown"),
            "type": "pylog",
            "level": record.levelname,
        }
        value = {
            "filename": record.filename,
            "lineno": record.lineno,
            "funcName": record.funcName,
            "message": record.getMessage(),
        }
        time_ns = str(int(record.created * 1000_000_000))
        self.buffer.put_nowait(
            Stream(
                stream=stream, values=[(time_ns, json.dumps(value, ensure_ascii=False))]
            )
        )
        if self.shouldFlush(record):
            self.flush()


class RotatingFileHandler(logging.handlers.RotatingFileHandler):
    def rotator(self, source, dest):
        pass


if __name__ == "__main__":
    import dotenv

    dotenv.load_dotenv()
    handler = LokiHandler(
        level=logging.DEBUG,
        flush_level="WARNING",
        capacity=10,
        host=os.getenv("LOKI_HOST"),
        user_id=os.getenv("LOKI_USER_ID"),
        api_key=os.getenv("LOKI_API_KEY"),
        verify=False,
    )

    logger = logging.getLogger("test")
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    logger.debug("test")
    logger.warning("test w")
    # time.sleep(9)
