# coding: utf-8
# IM 适配层

from lark_oapi import Client, im, JSON


class IMError(Exception):
    pass


class SendMessageError:
    pass


class IMAdapter:
    def __init__(self, client: Client):
        self.client = client

        self._chats: list[im.v1.model.ListChat] = []

    @property
    def chats(self):
        """获取用户或机器人所在的群列表"""
        if not self._chats:
            resp = self.client.im.v1.chat.list(im.v1.ListChatRequest.builder().build())
            assert resp.success()

            [self._chats.append(c) for c in resp.data.items]

        return self._chats

    def send_message(
        self, receive_id_type, receive_id, msg_type, content
    ) -> im.v1.CreateMessageResponse:
        """发送消息 oc_935401cad663f0bf845df98b3abd0cf6"""

        body = (
            im.v1.CreateMessageRequestBody.builder()
            .msg_type(msg_type)
            .content(content)
            .receive_id(receive_id)
            .build()
        )

        request = (
            im.v1.CreateMessageRequest.builder()
            .request_body(body)
            .receive_id_type(receive_id_type)
            .build()
        )

        return self.client.im.v1.message.create(request)

    def send_text_message_to_chat(
        self, chat_id, msg_content
    ) -> im.v1.CreateMessageResponse:
        """发送文本消息到群"""
        js = {"text": msg_content}
        return self.send_message("chat_id", chat_id, "text", JSON.marshal(js))

    def reply_message(self, parent_msg_id, content, msg_type: str, uuid: str = None):
        body = (
            im.v1.ReplyMessageRequestBody.builder()
            .msg_type(msg_type)
            .content(content)
            .build()
        )

        if uuid:
            body.uuid = uuid

        request = (
            im.v1.ReplyMessageRequest.builder()
            .request_body(body)
            .message_id(parent_msg_id)
            .build()
        )

        return self.client.im.v1.message.reply(request)

    def delete_message(self, message_id):
        """撤回消息"""
        request = im.v1.DeleteMessageRequest.builder().message_id(message_id).build()
