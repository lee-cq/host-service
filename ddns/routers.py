from fastapi import APIRouter, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel

router = APIRouter(
    prefix='/ddns'
)

DnspodClient = DnspodApi()


class ModelDomain(BaseModel):
    domain: str
    ipv6: str = None
    ipv4: str = None
    ttl: int = 600


@router.put('/update/{domain}')
def update(domain: str, data: ModelDomain):
    if domain != data.domain:
        return JSONResponse(status_code=401, content={"msg": "Error: Check Error."})
