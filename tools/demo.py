#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File Name  : demo.py
@Author     : LeeCQ
@Date-Time  : 2023/9/12 23:53
"""
import struct
import time
import os
import socket


def calc_checksum(src_bytes):
    """用于计算ICMP报文的校验和"""
    total = 0
    max_count = len(src_bytes)
    count = 0
    while count < max_count:
        val = src_bytes[count + 1] * 256 + src_bytes[count]
        total = total + val
        total = total & 0xFFFFFFFF
        count = count + 2

    if max_count < len(src_bytes):
        total = total + ord(src_bytes[len(src_bytes) - 1])
        total = total & 0xFFFFFFFF

    total = (total >> 16) + (total & 0xFFFF)
    total = total + (total >> 16)
    answer = ~total
    answer = answer & 0xFFFF
    answer = answer >> 8 | (answer << 8 & 0xFF00)
    return socket.htons(answer)


def sent_ping(
    icmp_socket, target_addr, identifier=os.getpid() & 0xFFFF, serial_num=0, data=None
):
    # 校验需要后面再计算，这里先设置为0
    ICMP_ECHO_REQUEST, code, checksum = 8, 0, 0
    # 初步打包ICMP头部
    header = struct.pack(
        "bbHHh", ICMP_ECHO_REQUEST, code, checksum, identifier, serial_num
    )
    # 打包选项数据
    if data:
        data = data.ljust(192, b"Q")
    else:
        data = struct.pack("d", time.time()).ljust(192, b"Q")
    checksum = calc_checksum(header + data)
    header = struct.pack(
        "bbHHh", ICMP_ECHO_REQUEST, code, checksum, identifier, serial_num
    )
    # 发送给目标地址，ICMP协议没有端口的概念端口可以随便填
    icmp_socket.sendto(header + data, (target_addr, 9999))


def receive_pong(icmp_socket, identifier=os.getpid() & 0xFFFF, serial_num=0, timeout=2):
    icmp_socket.settimeout(timeout)
    time_remaining = timeout
    while True:
        start_time = time.time()
        # 接收回送请求
        recv_packet, (ip, port) = icmp_socket.recvfrom(1024)
        time_received = time.time()
        time_spent = time_received - start_time
        # 前20字节是ip协议的ip头
        icmp_header = recv_packet[20:28]
        data = recv_packet[28:]
        (
            ICMP_Echo_Reply,
            code,
            checksum,
            identifier_reciver,
            serial_num_reciver,
        ) = struct.unpack("bbHHh", icmp_header)
        if identifier_reciver != identifier or serial_num != serial_num_reciver:
            # 不是当前自己发的包则忽略
            time_remaining -= time_spent
            if time_remaining <= 0:
                raise socket.timeout
            continue
        (time_sent,) = struct.unpack("d", data[: struct.calcsize("d")])
        return int((time_received - time_sent) * 1000)


_icmp_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)

sent_ping(_icmp_socket, "192.168.0.1")
try:
    delay, ip_received = receive_pong(_icmp_socket, timeout=2)
    print(f"延迟:{delay}ms，对方ip:{ip_received}")
except socket.timeout as e:
    print("超时")
