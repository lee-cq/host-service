# coding: utf8
"""Ping测试

对指定的地址执行Ping测试
"""
import logging
import os
import re
import subprocess
import asyncio
import sys
from typing import AsyncIterable

__all__ = ["ping", "a_ping", "a_ping_ttl"]

from tools import getencoding

logger = logging.getLogger("host-service.ping")

RE_PING_REST = {
    "win32": r"最短 = (.*?)ms，最长 = (.*?)ms，平均 = (.*?)ms",
    "linux": r"rtt min/avg/max/mdev = (.*?)/(.*?)/(.*?)/(.*?) ms",
}
RE_PING_TTL = {
    "win32": r"来自 .*? 的回复: 字节=\d+ 时间=(\d+)ms TTL=\d+",
    "linux": r"\d+ bytes from .*?: icmp_seq=\d+ ttl=\d+ time=(.*?) ms",
}


def popen(args: list):
    sp = subprocess.run(
        args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    sp.check_returncode()
    return sp.stdout.decode(getencoding())


def ping(host, timeout=60) -> tuple[float, float, float, float]:
    """

    :param host:
    :param timeout:
    :return: 平均值，最大值，最小值, 抖动
    """
    cmd = {
        "win32": ["ping", "-w", "1000", "-n", str(timeout), host],
        "linux": ["ping", "-w", str(timeout), host],
    }
    stdout = popen(cmd[sys.platform])
    if os.name == "nt":
        _min, _max, _avg = re.findall(RE_PING_REST[sys.platform], stdout)[0]
        return float(_avg), float(_max), float(_min), float(_max) - float(_min)
    else:
        _min, _avg, _max, _mdev = re.findall(RE_PING_REST[sys.platform], stdout)[0]
        return float(_avg), float(_max), float(_min), float(_mdev)


async def a_popen(cmd: str):
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    return stdout.decode(getencoding())


async def a_ping(host, timeout=60) -> tuple[float, float, float, float]:
    if os.name == "nt":
        cmd = f"ping -w 1000 -n {timeout} {host}"
        stdout = await a_popen(cmd)
        _min, _max, _avg = re.findall(RE_PING_REST[sys.platform], stdout)[0]
        return float(_avg), float(_max), float(_min), float(_max) - float(_min)
    else:
        stdout = await a_popen(f"ping -w {timeout} {host}")
        _min, _avg, _max, _mdev = re.findall(RE_PING_REST[sys.platform], stdout)[0]
        return float(_avg), float(_max), float(_min), float(_mdev)


async def a_ping_ttl(host, timeout=5) -> AsyncIterable[float]:
    """

    :param host:
    :param timeout: 单次超时时间
    :return:
    """
    logger.debug("ping %s timeout: %s", host, timeout)
    proc = await asyncio.create_subprocess_exec(
        "ping",
        host,
        "-i",
        str(timeout),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    logger.debug("ping %s pid: %s", host, proc.pid)
    while True:
        await asyncio.sleep(0.01)
        if proc.returncode is not None:
            logger.warning("ping %s return code: %s", host, proc.returncode)
            break
        try:
            line = (await proc.stdout.readline()).decode(getencoding())
            _re = re.findall(RE_PING_TTL[sys.platform], line)
            for r in _re:
                yield r
        except Exception as _e:
            logger.warning("has a Exception in the loop: %s", _e, exc_info=_e)
            proc.kill()


def test_ping():
    a = ping("localhost", timeout=4)
    print(a)


def test_a_ping():
    async def main():
        print(await a_ping("qq.com", timeout=1))

    asyncio.run(main())


def test_a_ping_ttl():
    async def main():
        async for i in a_ping_ttl("qq.com", timeout=1):
            print(i)

    asyncio.run(main())
