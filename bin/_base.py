#!/bin/env python3
# coding: utf-8

import os
import sys
import logging.config
from pathlib import Path

PACKAGE_PATH = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(PACKAGE_PATH))
os.chdir(PACKAGE_PATH)

LOG_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        "simple": {
            "formatter": "%(asctime)s %(name)s %(levelname)s - %(message)s"
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
            'level': 'DEBUG',

        },
        'file': {
            'class': 'logging.FileHandler',
            'formatter': 'simple',
            'filename': 'logs/test.log',
            'mode': 'a+',
            'level': 'INFO',
        }
    },

    'loggers': {
        'host-service': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
        }
    }
}

logging.config.dictConfig(LOG_CONFIG)
