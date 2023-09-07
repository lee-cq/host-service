import json
import logging
import socket
import time
import asyncio
from queue import Queue
from collections import defaultdict

from httpx import Client, AsyncClient
from httpx_ws import connect_ws, aconnect_ws, WebSocketNetworkError

from grafana.loki.aclient import ALokiClient
from grafana.loki.models import Stream

logger = logging.getLogger('host-service.grafana.clash')

HOSTNAME = socket.gethostname()


def transform_traffic(data: dict) -> dict:
    data['type'] = 'traffic'
    data['reportNode'] = HOSTNAME
    if 'source_type' in data:
        del data['source_type']
    return data


def transform_tracing(data: dict) -> dict:
    data['reportNode'] = HOSTNAME
    if 'metadata' in data:
        metadata = data.pop('metadata')
        data['metadata_dstip'] = metadata['destinationIP']
        data['metadata_dstport'] = metadata['destinationPort']
        data['metadata_host'] = metadata['host']
        data['metadata_network'] = metadata['network']
        data['metadata_srcip'] = metadata['sourceIP']
        data['metadata_srcport'] = metadata['sourcePort']
        data['metadata_type'] = metadata['type']
        data['metadata_dnsmode'] = metadata['dnsMode']
    return data


class Clash:

    def __init__(self, host, token):
        self.client = Client(
            base_url=f'http://{host}',
            params={'token': token},
        )
        self.queue_traffic = Queue()
        self.queue_profile = Queue()

    def ws_traffic(self):
        with connect_ws('/traffic', self.client, keepalive_ping_timeout_seconds=None) as ws:
            while True:
                self.queue_traffic.put(
                    transform_traffic(
                        ws.receive_json()
                    )
                )

    def ws_profile_tracing(self):
        pass


class AClash:

    def __init__(self, host, token):
        self.client = AsyncClient(
            base_url=f"http://{host}",
            params={'token': token},
        )
        self.queue = asyncio.Queue()

    async def _ws(self, url, transform_callback, queue):
        logger.info('Started receive %s ... ', url)
        async with aconnect_ws(url, self.client, keepalive_ping_timeout_seconds=None) as ws:
            logger.info('Connected to %s:%s .', self.client.base_url, url)
            while True:
                data = await ws.receive_json()
                data = transform_callback(data)
                await queue.put([str(time.time_ns()), data])
                logger.debug('added %s: %s', data['type'], data)

    async def _try_ws(self, url, transform_callback, queue):
        while True:
            start = time.time()
            try:
                await self._ws(url, transform_callback, queue)
            except WebSocketNetworkError:
                logger.warning('WebSocketNetworkError: This Connection lasts %.2f seconds', time.time() - start)

    async def ws_traffic(self):
        return asyncio.create_task(self._try_ws('/traffic', transform_traffic, self.queue))

    async def ws_profile_tracing(self):
        """创建一个task, 并持续的接受内容"""
        return asyncio.create_task(self._try_ws('/profile/tracing', transform_tracing, self.queue))

    async def create_streams(self) -> list[Stream]:
        streams = defaultdict(list)
        for _ in range(self.queue.qsize()):
            data = await self.queue.get()
            label_type = data[1]['type']
            data[1] = json.dumps(data[1])
            streams[label_type].append(data)

        return [Stream(stream={"type": k}, values=v) for k, v in streams.items()]

    async def push(self, loki_client: ALokiClient):
        while True:
            await asyncio.sleep(1)
            logger.debug('Queue size: %d', self.queue.qsize())
            streams = await self.create_streams()
            if streams:
                asyncio.create_task(
                    loki_client.push(streams)
                )

    async def run(self, loki_client: ALokiClient):
        await self.ws_traffic()
        await self.ws_profile_tracing()
        await self.push(loki_client)


def main_aclash():
    async def main():
        a = AClash('localhost:29090', '123456')
        await a.ws_traffic()
        await a.ws_profile_tracing()
        while True:
            await asyncio.sleep(1)
            print([a.model_dump() for a in await a.create_streams()])

    logging.basicConfig(level='INFO', )
    logger.info('Start .')
    asyncio.run(main())


def main_clash():
    """"""


if __name__ == '__main__':
    main_aclash()
