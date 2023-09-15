#!/bin/env python3
# coding: utf-8

import logging

import typer

# noinspection PyUnresolvedReferences
import _base as __

app = typer.Typer()
logger = logging.getLogger("host-service.bin.send-message")


@app.command()
def to_chat(chat_id, msg_content):
    from feishu.im_adapter import IMAdapter
    from feishu.client import client

    im = IMAdapter(client)
    resp = im.send_text_message_to_chat(chat_id, msg_content)
    logger.info(resp)


@app.command()
def to_hook(hook_id, msg_content, keyword=None, secret=None):
    from feishu.send_to_hook import HookBot

    im = HookBot(hook_id, keyword=keyword, secret=secret)
    resp = im.send_text(msg_content)
    logger.info(resp)


if __name__ == "__main__":
    app()
