import asyncio.subprocess
import os
import re
import subprocess
import locale
import time

from dotenv import load_dotenv

load_dotenv()


class Ping:
    RE_PING_WINDOWS = r'来自 (.*?) 的回复: 字节=.*? 时间=(.*?)ms TTL=.*'
    RE_PING_UBUNTU = r'\d* bytes from (.*?) .*?: icmp_seq=\d+ ttl=\d+ time=(.*?) ms'

    def __init__(self, host):
        self.host = host
        self.popen_ping = subprocess.Popen(
            ['ping', '-t', host],
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            universal_newlines=True,
            encoding=locale.getencoding()
        )

    async def run(self):
        while True:
            if self.popen_ping.poll() is not None:
                break
            res = re.findall(
                self.RE_PING_WINDOWS if os.name == 'nt' else self.RE_PING_UBUNTU,
                self.popen_ping.stdout.readline()
            )

            if res:
                ip, ttl = res[0]
                _time = str(time.time_ns())
                yield _time, (ip, ttl)
