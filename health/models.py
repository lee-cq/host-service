#!/bin/env python3

from pydantic import BaseModel


class ModelCheckConfig(BaseModel):
    """配置检测"""
    name: str
    type: str # HTTP / Ping / shell(Exit_code 0)
    target: str # HTTP: URL / Ping: IP/Domain / shell: bash
    timeout: int = 3 # 超时，默认3s

