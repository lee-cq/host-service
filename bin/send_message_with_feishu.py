#!/bin/env python3
# coding: utf-8

# noinspection PyUnresolvedReferences
import _base as __

import typer

app = typer.Typer()


@app.command()
def send_message(chat_id, msg_content):
    from feishu.im_adapter import IMAdapter
    from feishu.client import client

    im = IMAdapter(client)
    im.send_text_message_to_chat(
        chat_id, msg_content
    )


if __name__ == '__main__':
    app()
