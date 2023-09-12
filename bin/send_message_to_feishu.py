#!/bin/env python3
# coding: utf-8

import logging

import typer

# noinspection PyUnresolvedReferences
import _base as __

app = typer.Typer()
logger = logging.getLogger("host-service.bin.send-message")


@app.command()
def send_message(chat_id, msg_content):
    from feishu.im_adapter import IMAdapter
    from feishu.client import client

    im = IMAdapter(client)
    resp = im.send_text_message_to_chat(chat_id, msg_content)
    logger.info(resp)


if __name__ == "__main__":
    app()
