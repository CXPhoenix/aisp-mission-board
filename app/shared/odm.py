from configs import db_conf
from beanie import init_beanie, Document
from motor.motor_asyncio import AsyncIOMotorClient
import logging

console = logging.getLogger('uvicorn.error')


class MongoDbClient:
    def __init__(self) -> None:
        console.info("建立與 MongoDB 資料庫的連線...")
        self._client = AsyncIOMotorClient(
            host=db_conf.host,
            port=db_conf.port,
            username=db_conf.username,
            password=db_conf.password,
            authSource=db_conf.auth_source,
        )

    async def init_database_connection(
        self, database_name: str, documents: list[Document]=[]
    ) -> "MongoDbClient":
        await init_beanie(
            database=self._client[database_name], document_models=documents
        )
        console.info(f"已連線至 database {database_name}")
        return self

    def close_connection(self) -> None:
        console.info("正在關閉 MongoDB 連線...")
        self._client.close()
        console.info("MongoDB 連線已關閉。")
