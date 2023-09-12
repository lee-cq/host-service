#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File Name  : toots/ping.py
@Author     : LeeCQ
@Date-Time  : 2023/9/12 22:31

实现原理：https://blog.51cto.com/u_11866025/5714483#_441
"""
import time
import socket


def ping(host, port, timeout=5) -> float:
    """Ping主机并返回延迟时间"""
    icmp_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
    icmp_socket.settimeout(timeout)
    start_time = time.time()
    try:
        icmp_socket.connect((host, port))
    finally:
        icmp_socket.close()
        return time.time() - start_time


if __name__ == "__main__":
    print(ping("192.168.0.1"))
