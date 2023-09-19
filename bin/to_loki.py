#!/bin/env python3
# coding: utf8
"""更具配置将不同类型的信息推送到不同的目的地

"""
import asyncio
import logging
from pathlib import Path

import yaml

import _base
from grafana.push import Handler
from tools import gc_callback

logger = logging.getLogger("host-service.bin.to-loki")

_base.logging_configurator(
    name="to-loki",
    console_print=True,
    console_level="INFO" if _base.IS_SYSTEMD else "DEBUG",
    file_level="DEBUG" if _base.IS_SYSTEMD else "INFO",
)

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
    logger.info("Loaded Config File Success.")

    handle = Handler()
    for i in config_dict["inputs"]:
        i: dict
        type_ = i.pop("type")
        handle.register_input(type_, **i)
        logger.info("注册输入: %s, %s", type_, i)
    for o in config_dict["outputs"]:
        o: dict
        type_ = o.pop("type")
        handle.register_output(type_, **o)
        logger.info("注册输出: %s, %s", type_, o)

    asyncio.run(handle.start())


if __name__ == "__main__":
    import typer
    import gc

    gc.callbacks.append(gc_callback)

    typer.run(to_loki)
