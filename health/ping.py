# coding: utf8
"""Ping测试

对指定的地址执行Ping测试
"""
import os
import re
import subprocess

import asyncio

__all__ = ['ping', 'a_ping']


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


def ping(host, timeout=60) -> tuple[float, float, float, float]:
    """

    :param host:
    :param timeout:
    :return: 平均值，最大值，最小值, 抖动
    """
    return ping_windows(host, timeout) if os.name == 'nt' else ping_linux(host, timeout)


async def a_popen(cmd: str):
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    return stdout


async def a_ping_linux(host, timeout=60) -> tuple[float, float, float, float]:
    """

    :param host:
    :param timeout:
    :return: 平均值，最大值，最小值，抖动
    """
    stdout = await a_popen(f'ping -w {timeout} {host}')
    stdout = stdout.decode('utf8')
    _min, _avg, _max, _mdev = re.findall(r'rtt min/avg/max/mdev = (.*?)/(.*?)/(.*?)/(.*?) ms', stdout)[0]
    return float(_avg), float(_max), float(_min), float(_mdev)


async def a_ping_windows(host, timeout=60) -> tuple[float, float, float, float]:
    """

    :param host:
    :param timeout:
    :return: 平均值，最大值，最小值, 抖动
    """

    cmd = f'ping -w 1000 -n {timeout} {host}'
    stdout = await a_popen(cmd)
    stdout = stdout.decode('gbk')
    _min, _max, _avg = re.findall(r'最短 = (.*?)ms，最长 = (.*?)ms，平均 = (.*?)ms', stdout)[0]
    return float(_avg), float(_max), float(_min), float(_max) - float(_min)


async def a_ping(host, timeout=60) -> tuple[float, float, float, float]:
    return await (a_ping_windows(host, timeout) if os.name == 'nt' else a_ping_linux(host, timeout))


def test_ping():
    a = ping('10.1.1.1', timeout=4)
    print(a)


def test_a_ping():
    async def main():
        print(await a_ping('qq.com', timeout=1))

    asyncio.run(
        main()
    )
