# coding: utf8

from fastapi import APIRouter
from fastapi import WebSocket

from .models import ModelCheckConfig

router = APIRouter(prefix='/health')


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
