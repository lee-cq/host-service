from collections import namedtuple

from pydantic import BaseModel

LogValue = namedtuple('log_value', ['time_ns', 'line'])


class Stream(BaseModel):
    stream: dict
    values: list[LogValue]
