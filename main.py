import json
import time

from fastapi import FastAPI, Request, Response

from feishu.api_hook import router as feishu_api_hook_router
from feishu.decrypt import DecryptRequest

app = FastAPI(
    # root_path='/api/v1',
    # root_path_in_servers=False,
    title='FastAPI Demo',
    description='FastAPI Demo',
    version='1.0.0',
)


# @app.middleware("http")
# async def add_process_time_header(request: Request, call_next):
#     if request.url.path.startswith('/feishu/'):
#         print('Create New DecryptRequest')
#         request = DecryptRequest(request.scope, request.receive)
#         # print(await request.json())
#     response: Response = await call_next(request)
#     print('response', response.status_code, )
#     return response


app.include_router(feishu_api_hook_router)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
