import os

from fastapi import APIRouter, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from .dnspod import DnspodAPI

router = APIRouter()

DNSPOD_CLIENT = DnspodAPI(
    id_=os.getenv("HS_DNSPOD__ID"),
    token=os.getenv("HS_DNSPOD__TOKEN")
)


class ModelDomain(BaseModel):
    domain: str
    ipv6: str = None
    ipv4: str = None
    ttl: int = 600
    record_id: str = None


@router.put('/update/{domain}')
def update(domain: str, data: ModelDomain):
    if domain != data.domain:
        return JSONResponse(status_code=401, content={"msg": "Error: Check Error."})

    rr, domain = data.domain.split('.', maxsplit=1)
    if data.record_id is None:
        data.record_id = DNSPOD_CLIENT.record_list(

        )
    DNSPOD_CLIENT.record_update(

    )
