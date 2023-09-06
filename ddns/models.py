from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict


class RecordType(str, Enum):
    """记录类型"""
    A = 'A'
    AAAA = "AAAA"
    CNAME = "CNAME"
    TXT = "TXT"


class Record(BaseModel):
    id: str
    ttl: int
    value: str
    enable: int
    status: str  #
    updated_on: datetime
    record_type_v1: int  #
    name: str  # rr
    line: str  # 线路
    line_id: int  # 线路ID
    type: RecordType  # 记录类型枚举
    remark: str
    use_aqb: str

    model_config = ConfigDict(
        json_schema_extra={
            "id": "638200799",
            "ttl": "600",
            "value": "feafbc92f0264e4daa7e3edb41870afa",
            "enabled": "1",
            "status": "enable",
            "updated_on": "2020-08-04 16:34:53",
            "record_type_v1": "1",
            "name": "alidnscheck",
            "line": "默认",
            "line_id": "0",
            "type": "TXT",
            "weight": None,
            "monitor_status": "",
            "remark": "a - 阿里",
            "use_aqb": "no",
            "mx": "0"
        },
    )


class Status(BaseModel):
    code: int
    message: str
    created_at: datetime


class Domain(BaseModel):
    id: str
    name: str
    punycode: str
    grade: str
    owner: str
    ext_status: str
    ttl: int
    min_ttl: int
    dnspod_ns: list[str, ...]
    status: str
    can_handle_at_ns: bool

    model_config = ConfigDict(
        json_schema_extra={
            "id": "84259341",
            "name": "leecq.cn",
            "punycode": "leecq.cn",
            "grade": "DP_Free",
            "owner": "qcloud_uin_100010049611@qcloud.com",
            "ext_status": "",
            "ttl": 120,
            "min_ttl": 600,
            "dnspod_ns": [
                "geoff.dnspod.net",
                "trapezoid.dnspod.net"
            ],
            "status": "enable",
            "can_handle_at_ns": True
        },
    )


class Info(BaseModel):
    sub_domains: int
    record_total: int
    records_num: int


class RecordList(BaseModel):
    status: Status
    domain: Domain
    info: Info
    records: list[Record]
