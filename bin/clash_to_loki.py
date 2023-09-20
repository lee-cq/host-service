#!/bin/env python3
# coding: utf8
import asyncio
import json
import os
import socket

import _base
import typer
import pydantic_settings

from grafana.client_loki import LokiClient
from grafana.clash import AClash

_base.logging_configurator(
    name="clash_to_loki",
    console_print=True,
    console_level="INFO" if _base.IS_SYSTEMD else "DEBUG",
    file_level="DEBUG" if _base.IS_SYSTEMD else "INFO",
)
app = typer.Typer()


class Settings(pydantic_settings.BaseSettings):
    clash_host: str
    clash_token: str
    loki_host: str
    loki_user_id: str
    loki_api_key: str


@app.command()
def main(
    config_file: str = None,
    clash_host: str = None,
    clash_token: str = None,
    loki_host: str = None,
    loki_user_id: str = None,
    loki_api_key: str = None,
):
    if config_file:
        with open(config_file, "r", encoding="utf8") as f:
            config = json.loads(f.read())
            config: dict
        for k, v in config.items():
            if v:
                os.environ[k] = v

    if clash_host:
        os.environ["clash_host"] = clash_host
    if clash_token:
        os.environ["clash_token"] = clash_token
    if loki_host:
        os.environ["loki_host"] = loki_host
    if loki_user_id:
        os.environ["loki_user_id"] = loki_user_id
    if loki_host:
        os.environ["loki_api_key"] = loki_api_key

    s = Settings()
    loki_client = LokiClient(
        host=s.loki_host,
        user_id=s.loki_user_id,
        api_key=s.loki_api_key,
        verify=False,
        labels={"reportNode": socket.gethostname(), "app": "python-clash"},
    )

    asyncio.run(
        AClash(host=s.clash_host, token=s.clash_token).run_with_loki(loki_client)
    )


if __name__ == "__main__":
    app()
