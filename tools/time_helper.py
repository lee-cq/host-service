#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File Name  : time_helper.py
@Author     : LeeCQ
@Date-Time  : 2023/9/16 1:32
"""
import datetime
import time

# 东八区
tz = datetime.timezone(datetime.timedelta(hours=8))


def datetime_now() -> datetime:
    return datetime.datetime.now(tz=tz)


def timestamp_s() -> int:
    return int(time.time())


def timestamp_ms() -> int:
    return int(time.time() * 1000)


def timestamp_ns() -> int:
    if hasattr(time, "time_ns"):
        return time.time_ns()
    return int(time.time() * 1000000000)


def human_timedelta(seconds: int) -> str:
    return str(datetime.timedelta(seconds=seconds))