# coding: utf-8
"""
@File Name  : send_to_hook.py
@Author     : LeeCQ
@Date-Time  : 2023/9/15 14:40

发送消息web Hook机器人
"""
import base64
import hashlib
import hmac
import time

from httpx import post


class HookBot:
    """发送消息web Hook机器人"""

    def __init__(self, hook_id, keyword=None, secret=None):
        self.base_url = "https://open.feishu.cn/open-apis/bot/v2/hook/"
        self.hook_id = hook_id
        self.keyword = keyword
        self.secret = secret

    def gen_sign(self):
        """签名"""
        timestamp = int(time.time())
        string_to_sign = f"{timestamp}\n{self.secret}"
        hmac_code = hmac.new(
            string_to_sign.encode("utf-8"), digestmod=hashlib.sha256
        ).digest()
        return timestamp, base64.b64encode(hmac_code).decode("utf-8")

    def send_message(self, msg: dict):
        """发送消息"""
        if self.secret:
            msg["timestamp"], msg["sign"] = self.gen_sign()

        resp = post(self.base_url + self.hook_id, json=msg)
        return resp.status_code, resp.json()["msg"]

    def send_text(self, text: str):
        return self.send_message({"msg_type": "text", "content": {"text": text}})

    def test(self):
        """测试"""
        return self.send_text(f"test web hook , {self.hook_id}")
