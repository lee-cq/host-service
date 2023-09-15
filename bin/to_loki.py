#!/bin/env python3
# coding: utf8
"""更具配置将不同类型的信息推送到不同的目的地

"""
import asyncio
from pathlib import Path

import yaml

from grafana.push import Handler

config = """version: 1

inputs:
  - type: clash
    host: hostname
    token:
  - type: ping
    host: hostname:port
  - type: tailscale
    tsnet: tsnet
    api_key: api_key

outputs:
  - type: loki
    host: hostname
    user_id: user_id
    api_key: api_key
  - type: file
    filename: filename.log
    encoding: utf-8
    mode: a+
"""


def to_loki(file: Path):
    config_dict = yaml.safe_load(file.read_text(encoding="utf8"))

    hardle = Handler()
    for i in config_dict["inputs"]:
        i: dict
        type_ = i.pop("type")
        hardle.register_input(type_, **i)
    for o in config_dict["outputs"]:
        o: dict
        type_ = o.pop("type")
        hardle.register_input(type_, **o)

    asyncio.run(hardle.start())


if __name__ == "__main__":
    import typer

    typer.run(to_loki)
