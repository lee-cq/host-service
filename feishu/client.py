# coding: utf-8
# 客户端
import os
from pathlib import Path

import lark_oapi as lark

import dotenv

dotenv.load_dotenv(Path(__file__).parent.parent.joinpath('.env'))

app_id = os.getenv('HS_FS__APPID')
app_secret = os.getenv('HS_FS__APPSECRET')
app_timeout = 3

__all__ = [
    "app_id", "app_secret", "app_timeout",
    "client"
]

client = lark.Client.builder() \
    .app_id(app_id) \
    .app_secret(app_secret) \
    .timeout(app_timeout) \
    .build()
