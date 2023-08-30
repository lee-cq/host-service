#! encoding: utf8
from uuid import UUID

from pydantic import BaseModel, Field


class ModelEncrypt(BaseModel):
    encrypt: str


class ModelVerify(BaseModel):
    challenge: str | None
    token: str | None
    type: str | None


class ModelUser(BaseModel):
    user_id: str
    name: str
    open_id: str


class ModelOperator(BaseModel):
    user_id: str
    open_id: str


class ModelEventV1Connect(BaseModel):
    app_id: str
    chat_id: str
    operator: ModelOperator
    tenant_key: str
    type: str
    user: ModelUser


class ModelEventV1(BaseModel):
    type: str
    ts: int
    uuid: UUID
    token: str
    event: ModelEventV1Connect

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "ts": "1502199207.7171419",
                    "uuid": "bc447199585340d1f3728d26b1c0297a",
                    "token": "41a9425ea7df4536a7623e38fa321bae",
                    "type": "event_callback",
                    "event": {
                        "app_id": "cli_9c8609450f78d102",
                        "chat_id": "oc_26b66a5eb603162b849f91bcd8815b20",
                        "operator": {
                            "open_id": "ou_2d2c0399b53d06fd195bb393cd1e38f2",
                            "user_id": "gfa21d92"
                        },
                        "tenant_key": "736588c9260f175c",
                        "type": "p2p_chat_create",
                        "user": {
                            "name": "user_name",
                            "open_id": "ou_7dede290d6a27698b969a7fd70ca53da",
                            "user_id": "gfa21d92"
                        }
                    }
                }
            ]
        }
    }


class ModelEventV2Header(BaseModel):
    event_id: str
    token: str
    create_time: int
    event_type: str
    tenant_key: str
    app_id: str


class ModelEventV2MessageSenderID(BaseModel):
    open_id: str
    union_id: str
    user_id: str = None


class ModelEventV2MessageSender(BaseModel):
    sender_id: ModelEventV2MessageSenderID
    sender_type: str
    tenant_key: str


class ModelEventV2MessageMention(BaseModel):
    key: str  # mention key
    id: ModelUser  # User id
    name: str  # User name
    tenant_key: str  # tenant key


class ModelEventV2MessageContent(BaseModel):
    message_id: str  # 消息的open_message_id，
    root_id: str = None  # 根消息id，用于回复消息场景，说明参见：消息ID说明
    parent_id: str = None  # 父消息的id，用于回复消息场景，说明参见：消息ID说明
    create_time: int  # 消息发送时间（毫秒）
    chat_id: str  # 群组ID
    chat_type: str  # 群组类型，group：群组；p2p：私聊
    # 各个消息内容https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/im-v1/message/events/message_content
    content: dict  # 消息内容 JSON格式
    mentions: list[ModelEventV2MessageMention] = None  # @的用户列表


class ModelEventV2Message(BaseModel):
    sender: ModelEventV2MessageSender
    message: ModelEventV2MessageContent


class ModelEventV2(BaseModel):
    # alias = "schema"
    schema_2: str = Field(alias="schema")
    header: ModelEventV2Header
    event: dict

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "schema": "2.0",
                    "header": {
                        "event_id": "f7984f25108f8137722bb63cee927e66",
                        "token": "066zT6pS4QCbgj5Do145GfDbbagCHGgF",
                        "create_time": "1603977298000000",
                        "event_type": "contact.user_group.created_v3",
                        "tenant_key": "xxxxxxx",
                        "app_id": "cli_xxxxxxxx",
                    },
                    "event": {
                    }
                }
            ]
        }
    }
