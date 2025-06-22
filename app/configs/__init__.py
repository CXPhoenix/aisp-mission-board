import typing

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from uvicorn.config import logger

class EnvConf(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=False, extra="ignore")


class DbConf(EnvConf):
    model_config = SettingsConfigDict(env_prefix="MONGODB_")

    host: str = "mongo"
    port: int = 27017
    initdb_root_username: str = "<your-username>"
    initdb_root_password: str = "<your-password>"
    auth_source: str = "admin"


class SystemConf(EnvConf):
    model_config = SettingsConfigDict(env_prefix="SYSTEM_")
    
    session_secret: str = "<your-session-secret>"


class AppConf(EnvConf):
    model_config = SettingsConfigDict(env_prefix="APP_")
    
    userdb: str = "<your-userdb>"
    admins: str | list[str] = []
    
    @field_validator('admins', mode='after')
    @classmethod
    def seperate_admin_list(cls, v: str) -> list[str]:
            if isinstance(v, str):
                return v.split(':')
            return v


db_conf = DbConf()
sys_conf = SystemConf()
app_conf = AppConf()

__all__ = [db_conf, sys_conf, app_conf]