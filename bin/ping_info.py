#!/bin/env python3
# coding: utf-8
import subprocess
import time
import logging

import typer

# noinspection PyUnresolvedReferences
import _base as __
from health.ping import ping

app = typer.Typer()

logger = logging.getLogger("host-service.bin.ping-info")


@app.command()
def main(host, timeout=60, chat_id="oc_935401cad663f0bf845df98b3abd0cf6"):
    """"""
    date = time.strftime('%Y-%m-%d %H:%M:%S')
    try:
        _avg, _max, _min, _mdev = ping(host, timeout)
        message = f"与 {host}， 从{date}开始的{timeout}秒中的网络状况：\n" \
                  f"平均值: {_avg} ms\n" \
                  f"最大值: {_max} ms\n" \
                  f"最小值: {_min} ms\n" \
                  f"网络抖动: {_mdev} ms"
    except (subprocess.CalledProcessError, IndexError) as _e:
        message = f"Error: {_e}"

    logger.info(message)

    from feishu.im_adapter import IMAdapter
    from feishu.client import client

    im = IMAdapter(client)
    resp = im.send_text_message_to_chat(
        chat_id, str(message)
    )

    if not resp.success():
        logger.error(resp.raw.content)
    else:
        logger.info(resp.raw.content)


if __name__ == '__main__':
    app()
