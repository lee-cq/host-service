#!/bin/env python3
# coding: utf-8

import os
import sys
import logging
import logging.config
from pathlib import Path
from dotenv import load_dotenv


logger = logging.getLogger("host-service.bin._base")

WORKDIR = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(WORKDIR))
os.chdir(WORKDIR)

load_dotenv()

# 创建日志目录
LOG_DIR = WORKDIR.joinpath("logs")
if not LOG_DIR.exists():
    LOG_DIR.mkdir()


def is_systemd() -> bool:
    """判断是否是systemd"""
    if os.getenv("INVOCATION_ID"):
        return True
    if os.getppid() == "1":
        return True
    return False


IS_SYSTEMD = is_systemd()


def logging_configurator(
    name=__name__,
    console_print=True,
    console_level="DEBUG",
    file_level="INFO",
):
    """创建日志配置"""
    handlers = ["file"]
    if console_print:
        handlers.append("console")

    log_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "simple": {"format": "%(asctime)s %(name)s %(levelname)s - %(message)s"},
            "systemd": {"format": "%(name)s %(levelname)s - %(message)s"},
            "error": {
                "format": (
                    "TIME      = %(asctime)s \n"
                    "FILE_NAME = %(filename)s \n"
                    "FUNC_NAME = %(funcName)s \n"
                    "LINE_NO   = %(lineno)d \n"
                    "LEVEL     = %(levelname)s \n"
                    "MESSAGE   = %(message)s \n"
                    "EXCEPTION = %(exc_info)s \n"
                    "+------------------------------------------+"
                )
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "systemd" if is_systemd() else "simple",
                "level": console_level,
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "simple",
                "level": file_level,
                "filename": f"logs/{name}.log",
                "mode": "a+",
                "maxBytes": 50 * 1024**2,
                "backupCount": 5,
            },
            "file_warning": {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "error",
                "level": "WARNING",
                "filename": f"logs/{name}-error.log",
                "mode": "a+",
                "maxBytes": 50 * 1024**2,
                "backupCount": 5,
            },
            "root_handler": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "DEBUG",
                "formatter": "simple",
                "filename": "logs/root.log",
                "mode": "a+",
                "maxBytes": 50 * 1024**2,
                "backupCount": 5,
            },
            "loki": {
                "class": "tools.logging_handle.LokiHandler",
                "formatter": "simple",
                "level": "DEBUG",
                "flush_level": "WARNING",
                "capacity": 50,
                "host": os.getenv("LOKI_HOST"),
                "user_id": os.getenv("LOKI_USER_ID"),
                "api_key": os.getenv("LOKI_API_KEY"),
                "verify": False,
            },
        },
        "loggers": {
            "host-service": {
                "handlers": handlers,
                "level": "DEBUG",
            }
        },
        "root": {
            "handlers": ["root_handler", "file_warning", "loki"],
            "level": "DEBUG",
        },
    }
    logging.config.dictConfig(log_config)
    logger.warning(f"Restart {name} ......")


if __name__ == "__main__":
    logging_configurator()
    logger = logging.getLogger("host-service")
    print(logger.handlers)
