from pydantic_settings import BaseSettings, SettingsConfigDict


class EnvConf(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=False, extra="ignore")

class DbConf(EnvConf):
    model_config = SettingsConfigDict(env_prefix='MONGODB_')
    
    host: str = "mongo"
    port: int = 27017
    username: str = "username"
    password: str = "password"
    auth_source: str = "admin"

class SystemConf(EnvConf):
    # TODO: Set Configurations
    ...

db_conf = DbConf()