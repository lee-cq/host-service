from unittest import TestCase

from feishu.client import client
from feishu.im_adapter import IMAdapter


class TestFeishuIM(TestCase):
    def test_chats(self):
        assert IMAdapter(client).chats

    def test_send_text_message_to_chat(self):
        assert IMAdapter(client).send_text_message_to_chat('oc_935401cad663f0bf845df98b3abd0cf6', 'unittest').success()

    def test_send_text_message_to_chat_more_line(self):
        assert IMAdapter(client).send_text_message_to_chat(
            'oc_935401cad663f0bf845df98b3abd0cf6',
            "unittest\nmore\nline\n!@#$%^&*()1234567890{}[]:':,.<>/?"
        )