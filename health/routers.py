# coding: utf8
import time
import threading

from fastapi import APIRouter, Response
from lark_oapi import JSON

from feishu.client import client
from feishu.im_adapter import IMAdapter
from .models import ModelCheckConfig
from .ping import a_ping

router = APIRouter()


@router.post('/config')
async def add_check(config: ModelCheckConfig):
    pass


@router.put("/config")
async def change_check(config: ModelCheckConfig):
    pass


@router.get("/configs")
async def list_config():
    pass


@router.get('/status')
def status():
    return


@router.get('/ping')
async def ping(host: str, timeout: int = 10, chat_id: str = "oc_935401cad663f0bf845df98b3abd0cf6"):
    async def _ping() -> str:
        date = time.strftime('%Y-%m-%d %H:%M:%S')
        try:
            _avg, _max, _min, _mdev = await a_ping(host, timeout)
            message = f"与 {host}， 从{date}开始的{timeout}秒中的网络状况：\n" \
                      f"平均值: {_avg} ms\n" \
                      f"最大值: {_max} ms\n" \
                      f"最小值: {_min} ms\n" \
                      f"网络抖动: {_mdev} ms"
        except () as _e:
            message = f"Error: {_e}"

        resp = IMAdapter(client).send_text_message_to_chat(
            chat_id, message
        )
        return JSON.marshal(resp)

    if timeout <= 5:
        return await _ping()

    threading.Thread(name=f"ping-{host}", target=_ping)
    return Response(status_code=201, content={
        'action': "ping",
        'host': host,
        "timeout": timeout,
        "message": "正在统计"
    })
