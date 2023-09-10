import os
import re
import subprocess
import locale
import time

from dotenv import load_dotenv

from client_graphite import Grafana

load_dotenv()

URL = os.getenv('GRAFANA__URL')
USER_ID = os.getenv('GRAFANA__USER_ID')
API_KEY = os.getenv('GRAFANA__API_KEY')

RE_PING_WINDOWS = r'来自 (.*?) 的回复: 字节=.*? 时间=(.*?)ms TTL=.*'
RE_PING_UBUNTU = r'\d* bytes from (.*?) .*?: icmp_seq=\d+ ttl=\d+ time=(.*?) ms'

client = Grafana(URL, USER_ID, API_KEY)

pp = subprocess.Popen(
    ['ping', '-t', 'qq.com'],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    universal_newlines=True,
    encoding=locale.getencoding()
)

while True:
    if pp.poll() is not None:
        break
    res = re.findall(RE_PING_WINDOWS, pp.stdout.readline())
    if res:
        ip, ttl = res[0]
        _time = int(time.time() * 1000)

        client.push(
            {
                "name": "host-service.ping",
                "interval": 1,
                "value": float(ttl),
                "tags": [f"ip={ip}", "source=grafana_cloud_docs"],
                "time": _time
            }
        )
    print(client.total)

client.join()
