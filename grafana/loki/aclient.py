import json
import logging
from gzip import compress

from httpx import AsyncClient
from pydantic import BaseModel

from .common import LokiClientBase, LokiPushBase
from .models import Stream, LogValue

logger = logging.getLogger("host-service.grafana.loki")


class ALokiClient(LokiClientBase):

    def __init__(self, host, user_id, api_key, verify=True, **kwargs):
        self.client = AsyncClient(
            base_url=f'https://{host}',
            auth=(user_id, api_key),
            # headers={'Authorization': f'Bearer {user_id}:{api_key}'},
            verify=verify,
            **kwargs
        )

    async def push(self, data: list[Stream | dict]) -> int:
        """Push消息, 返回成功推送的消息数量"""
        lens_data = sum(len(_.values) for _ in data)
        data = {'streams': [i.model_dump() for i in data if isinstance(i, BaseModel)]}
        url = '/loki/api/v1/push'
        headers = {
            "Content-Type": "application/json",
            "Content-Encoding": "gzip"
        }
        data = compress(json.dumps(data).encode(), 9)  # 压缩数据

        resp = await self.client.post(url, content=data, headers=headers)
        if resp.status_code == 204:
            logger.debug('Pushed Success: %d, data size: %d', lens_data, len(data))
            return lens_data
        logger.warning('Loki push Error, code: %d.', resp.status_code)
        logger.debug("loki push Error, code %d, Msg: %s", resp.status_code, resp.text)
        return 0


class ALokiPush(ALokiClient, LokiPushBase):

    def __init__(self, host, user_id, api_key, **kwargs):
        super().__init__(host, user_id, api_key, **kwargs)

        self._labels = {}

    async def push(self, data: list[LogValue]) -> int:
        data = Stream(
            stream=self._labels,
            values=data
        )
        return await super().push([data])
