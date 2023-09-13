#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File Name  : bin/tailscale_to_loki.py
@Author     : LeeCQ
@Date-Time  : 2023/9/12 14:29

推送tailscale的连接状态到loki

"""
import asyncio
import os
import logging
import socket
from pathlib import Path

import _base
import typer

from grafana.client_loki import ALokiClient
from grafana.tailsacle import Tailscale

app = typer.Typer()

logger = logging.getLogger("host-service.bin.create-service")

_base.logging_configurator(
    name="tailscale_to_loki",
    console_print=True,
    console_level="INFO" if _base.IS_SYSTEMD else "DEBUG",
    file_level="DEBUG" if _base.IS_SYSTEMD else "INFO",
)


@app.command()
def main(
    tsnet: str = None,
    api_key: str = None,
    loki_host: str = None,
    loki_user_id: str = None,
    loki_api_key: str = None,
):
    loki_client = ALokiClient(
        host=loki_host,
        user_id=loki_user_id,
        api_key=loki_api_key,
        verify=False,
        labels={"reportNode": socket.gethostname(), "app": "python-tailscale"},
    )

    asyncio.run(Tailscale(tsnet, api_key).run_with_loki(loki_client))


if __name__ == "__main__":
    app()
