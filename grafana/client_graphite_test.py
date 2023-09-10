import os
import time

from dotenv import load_dotenv

from .client_graphite import GraphiteClient

load_dotenv()

URL = os.getenv("GRAFANA__URL")
USER_ID = os.getenv("GRAFANA__USER_ID")
API_KEY = os.getenv("GRAFANA__API_KEY")


def test_grafana_post():
    data = {
        "name": "test.metric.unittest",
        "tags": ["source=python", "logs=host-service.grafana"],
        "interval": 1,
        "value": 12.345,
        "time": int(time.time() * 1000),
    }
    _g = GraphiteClient(URL, USER_ID, API_KEY)
    resp = _g.client.post(
        URL,
        json=[data],
    )
    assert resp.status_code == 200, resp.text


def test_grafana_push():
    assert False


def test_grafana_pushes():
    assert False
