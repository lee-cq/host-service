#!/bin/env python3
# coding: utf-8
import os
import typing

from fastapi import APIRouter, Request, Response
from fastapi.routing import APIRoute

from lark_oapi.event.dispatcher_handler import EventDispatcherHandler
from lark_oapi.core.model.raw_response import RawResponse
from lark_oapi.core.model.raw_request import RawRequest
from lark_oapi.core import JSON as LARK_JSON, LogLevel
from lark_oapi.api.im.v1 import P2ImMessageReceiveV1

import dotenv

dotenv.load_dotenv()

router = APIRouter(
    tags=['feishu', 'hook'],
)


def do_p2_im_message_receive_v1(data: P2ImMessageReceiveV1) -> None:
    """返回"""
    with open("received_messages.txt", 'a', encoding='utf8') as ff:
        ff.write(LARK_JSON.marshal(data))

    print("data", )


# 监听操作器
handler = EventDispatcherHandler.builder(
    encrypt_key=os.getenv("HS_FS_EVENT_ENCRYPT") or os.getenv("ENCRYPT_KEY"),
    verification_token=os.getenv("HS_FS_EVENT_VERIFYTOKEN") or os.getenv("VERIFICATION_TOKEN"),
    level=LogLevel.DEBUG
).register_p2_im_message_receive_v1(do_p2_im_message_receive_v1) \
    .build()


class EventRoute(APIRoute):
    """适用于FastAPI <--> lark-oapi.event 的适配器路由"""

    def get_route_handler(self) -> typing.Callable:
        async def parse_req(request: Request) -> RawRequest:
            req = RawRequest()
            req.uri = request.url.path
            req.body = await request.body()
            req.headers = {k.title(): v for k, v in request.headers.items()}

            return req

        async def custom_route_handler(request: Request) -> Response:
            resp: RawResponse = handler.do(await parse_req(request))  # 事件解析
            request._body = resp.content
            return Response(
                content=resp.content,
                status_code=resp.status_code,
                headers=resp.headers
            )

        return custom_route_handler


router.route_class = EventRoute


@router.post("")
def event():
    """仅提供路由占位，全部的操作在适配器路由中实现"""
    pass


if __name__ == "__main__":
    import uvicorn
    from fastapi import FastAPI

    app = FastAPI(title='FastAPI Demo',
                  description='FastAPI Demo',
                  version='1.0.0',
                  )
    app.include_router(router)
    uvicorn.run(app=app, host='0.0.0.0', port=58000, )
