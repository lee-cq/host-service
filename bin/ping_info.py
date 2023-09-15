#!/bin/env python3
# coding: utf-8
import subprocess
import time
import logging

import typer


import _base
from health.ping import ping

app = typer.Typer()

logger = logging.getLogger("host-service.bin.ping-info")

_base.logging_configurator(
    name="clash_to_loki",
    console_print=True,
    console_level="INFO" if _base.IS_SYSTEMD else "DEBUG",
    file_level="DEBUG" if _base.IS_SYSTEMD else "INFO",
)


@app.command()
def main(
    host,
    timeout: int = 60,
    hook_id: str = None,
    keyword: str = None,
    secret: str = None,
):
    """"""
    date = time.strftime("%Y-%m-%d %H:%M:%S")
    try:
        _avg, _max, _min, _mdev = ping(host, timeout)
        message = (
            f"与 {host}， 从{date}开始的{timeout}秒中的网络状况：\n"
            f"平均值: {_avg} ms\n"
            f"最大值: {_max} ms\n"
            f"最小值: {_min} ms\n"
            f"网络抖动: {_mdev} ms"
        )
    except (subprocess.CalledProcessError, IndexError) as _e:
        message = f"Error: {_e}"

    logger.info(message)

    from feishu.send_to_hook import HookBot

    im = HookBot(hook_id, keyword=keyword, secret=secret)
    resp = im.send_text(message)
    logger.info(resp)


if __name__ == "__main__":
    app()
