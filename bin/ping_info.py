#!/bin/env python3
# coding: utf-8
import re
import subprocess
import time

# noinspection PyUnresolvedReferences
import _base as __

import os

import typer

app = typer.Typer()


def popen(args: list):
    sp = subprocess.run(
        args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    sp.check_returncode()
    return sp.stdout


def ping_linux(host, timeout=60) -> tuple[float, float, float, float]:
    """

    :param host:
    :param timeout:
    :return: 平均值，最大值，最小值，抖动
    """

    stdout = popen(["ping", "-w", str(timeout), host]).decode('utf8')
    _min, _avg, _max, _mdev = re.findall(r'rtt min/avg/max/mdev = (.*?)/(.*?)/(.*?)/(.*?) ms', stdout)[0]
    return float(_avg), float(_max), float(_min), float(_mdev)


def ping_windows(host, timeout=60) -> tuple[float, float, float, float]:
    """

    :param host:
    :param timeout:
    :return: 平均值，最大值，最小值, 抖动
    """
    stdout = popen(["ping", '-w', '1000', '-n', str(timeout), host]).decode('gbk')
    _min, _max, _avg = re.findall(r'最短 = (.*?)ms，最长 = (.*?)ms，平均 = (.*?)ms', stdout)[0]
    return float(_avg), float(_max), float(_min), float(_max) - float(_min)


@app.command()
def main(host, timeout=60, chat_id="oc_935401cad663f0bf845df98b3abd0cf6"):
    """"""
    date = time.strftime('%Y-%m-%d %H:%M:%S')
    try:
        _avg, _max, _min, _mdev = ping_windows(host, timeout) if os.name == 'nt' else ping_linux(host, timeout)
        message = f"与 {host}， 从{date}开始的{timeout}秒中的网络状况：\n" \
                  f"平均值: {_avg} ms\n" \
                  f"最大值: {_max} ms\n" \
                  f"最小值: {_min} ms\n" \
                  f"网络抖动: {_mdev} ms"
    except (subprocess.CalledProcessError, IndexError) as _e:
        message = f"Error: {_e}"

    print(message)

    from feishu.im_adapter import IMAdapter
    from feishu.client import client

    im = IMAdapter(client)
    resp = im.send_text_message_to_chat(
        chat_id, str(message)
    )

    if not resp.success():
        print(resp.raw.content)


if __name__ == '__main__':
    app()
