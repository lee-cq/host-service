from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import (
    BaseModel,
    Field,
)


class SettingsMysql(BaseSettings):
    """"""
    host: str
    port: int = 3306
    username: str
    password: str
    charset: str = "utf-8"
    database: str


class SettingsFeishu(BaseModel):
    """"""
    app_id: str = Field("", alias='APPID')
    app_secret: str = Field("", alias="APPSECRET")
    event_encrypt: str = Field(alias="EVENT_ENCRYPT")
    event_verify_token: str = Field("", alias="EVENT_VERIFYTOKEN")


class SettingsDnspod(BaseModel):
    id: str
    token: str


class Settings(BaseSettings):
    """"""
    model_config = SettingsConfigDict(
        env_prefix='hs_',
        env_file=".env",
        env_nested_delimiter="__",
        env_file_encoding='utf-8',
    )

    mysql: SettingsMysql
    fs: SettingsFeishu
    dnspod: SettingsDnspod


config = Settings().model_dump_json(indent=2)
print(config)
