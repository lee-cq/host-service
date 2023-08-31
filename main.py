from fastapi import FastAPI
from feishu.api_hook import router as feishu_api_hook_router
from feishu.event import router as feishu_event_router
from health.routers import router as health_router

app = FastAPI(
    # root_path='/api/v1',
    # root_path_in_servers=False,
    title='FastAPI Demo',
    description='FastAPI Demo',
    version='1.0.0',
)

app.include_router(feishu_event_router, prefix='/feishu_event', )
app.include_router(feishu_api_hook_router, prefix='/feishu', )
app.include_router(health_router, prefix='/health', )


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
