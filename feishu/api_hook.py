# encoding: utf-8
# Desc: Feishu API
# Date: 2021-04-25

from fastapi import APIRouter, Body

from feishu.model import ModelEncrypt, ModelVerify
from feishu.decrypt import DecryptRoute

router = APIRouter(
    prefix='/feishu',
    tags=['feishu', 'hook'],
)

router.route_class = DecryptRoute


@router.get("/test")
async def test():
    return {"ok": True}


@router.post("/verify")
async def verify(ver: ModelVerify):
    return {
        "challenge": ver.challenge
    }

