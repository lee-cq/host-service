import json
import time

from fastapi import FastAPI
from feishu.api_hook import router as feishu_api_hook_router
from feishu.event import router as feishu_event_router


app = FastAPI(
    # root_path='/api/v1',
    # root_path_in_servers=False,
    title='FastAPI Demo',
    description='FastAPI Demo',
    version='1.0.0',
)


app.include_router(feishu_event_router)
app.include_router(feishu_api_hook_router)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
