import typing

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class EnvConf(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=False, extra="ignore")


class DbConf(EnvConf):
    model_config = SettingsConfigDict(env_prefix="MONGODB_")

    host: str = "mongo"
    port: int = 27017
    username: str = "<your-username>"
    password: str = "<your-password>"
    auth_source: str = "admin"


class SystemConf(EnvConf):
    model_config = SettingsConfigDict(env_prefix="SYSTEM_")

    session_secret: str = "<your-session-secret>"


class AppConf(EnvConf):
    model_config = SettingsConfigDict(env_prefix="APP_")

    title: str = "<your-app-title>"
    userdb: str = "<your-userdb>"
    malldb: str = "<your-malldb>"
    recorddb: str = "<your-recorddb>"
    mission: str = "<your-missiondb>"  # 這個會升級
    admins: str | list[str] = []

    @field_validator("admins", mode="after")
    @classmethod
    def seperate_admin_list(cls, v: str) -> list[str]:
        if isinstance(v, str):
            return v.split(":")
        return v


db_conf = DbConf()
sys_conf = SystemConf()
app_conf = AppConf()

__all__ = [db_conf, sys_conf, app_conf]
