from beanie import Document, init_beanie
from configs import db_conf
from motor.motor_asyncio import AsyncIOMotorClient

from .logs import console


class MongoDbClient:
    def __init__(
        self,
        *,
        host: str = db_conf.host,
        port: int = db_conf.port,
        username: str = db_conf.username,
        password: str = db_conf.password,
        auth_source: str = db_conf.auth_source,
    ) -> None:
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self._auth_source = auth_source
        self._client = None

    def build_connection(self) -> "MongoDbClient":
        self._client = AsyncIOMotorClient(
            host=self._host,
            port=self._port,
            username=self._username,
            password=self._password,
            authSource=self._auth_source,
        )
        console.info("成功建立與 MongoDB 資料庫的連線")
        return self

    async def init_database_connection(
        self, database_name: str, documents: list[Document] = []
    ) -> "MongoDbClient":
        if self._client is None:
            console.error(
                "client can't be None. Use `MongoDbClient().build_connection()` first."
            )
            raise ValueError(
                "client can't be None. Use `MongoDbClient().build_connection()` first."
            )
        await init_beanie(
            database=self._client[database_name], document_models=documents
        )
        console.info(
            f"已連線至 database '{database_name}' 的 Collections: {', '.join(map(lambda d: f"'{d.get_settings().name}'", documents))}"
        )
        return self

    def close_connection(self) -> None:
        console.info("正在關閉 MongoDB 連線...")
        self._client.close()
        console.info("MongoDB 連線已關閉。")
