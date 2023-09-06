import json
import os

import pytest
from dotenv import load_dotenv

from dnspod import DnspodAPI

load_dotenv()

DNSPOD_CLIENT = DnspodAPI(
    id_=os.getenv("HS_DNSPOD__ID"),
    token=os.getenv("HS_DNSPOD__TOKEN")
)


def test_p1():
    print('\n', json.dumps(DNSPOD_CLIENT.record_list('leecq.cn'), indent=2, ensure_ascii=False))


if __name__ == '__main__':
    pytest.main()
