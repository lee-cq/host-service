import logging

from httpx import Client
from pydantic import BaseModel

from .common import LokiClientBase, LokiPushBase
from .models import Stream, LogValue

logger = logging.getLogger("host-service.grafana.loki")


class LokiClient(LokiClientBase):

    def __init__(self, host, user_id, api_key, verify=True, **kwargs):
        self.client = Client(
            base_url=f'https://{host}',
            auth=(user_id, api_key),
            # headers={'Authorization': f'Bearer {user_id}:{api_key}'},
            verify=verify,
            **kwargs
        )

    def push(self, data: list[Stream]) -> int:
        """Push消息, 返回成功推送的消息数量"""
        lens_data = sum(len(_.values) for _ in data)
        data = {'streams': [i.model_dump() for i in data if isinstance(i, BaseModel)]}
        url = '/loki/api/v1/push'
        resp = self.client.post(url, json=data, )
        if resp.status_code == 204:
            return lens_data
        logger.warning('Loki push Error, code: %d.', resp.status_code)
        logger.debug("loki push Error, code %d, Msg: %s", resp.status_code, resp.text)
        return 0


class ALokiPush(LokiClient, LokiPushBase):

    def __init__(self, host, user_id, api_key, **kwargs):
        super().__init__(host, user_id, api_key, **kwargs)

        self._labels = {}

    def push(self, data: list[LogValue]) -> int:
        data = Stream(
            stream=self._labels,
            values=data
        )
        return super().push([data])
