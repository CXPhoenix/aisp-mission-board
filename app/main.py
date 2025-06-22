from contextlib import asynccontextmanager

from fastapi import FastAPI
from configs import sys_conf, app_conf
from shared import MongoDbClient, SessionMiddleware

# Open API Doc 參數設定
DOCS_URL = None  # default is `/docs`
REDOC_URL = None  # default is `/redoc`
OPENAPI_URL = None  # default is `/openapi.json`

# Server 開始與結束時的事件設定
@asynccontextmanager
async def lifespan(app: FastAPI):
    # TODO: Model Import
    mclient = MongoDbClient()
    yield
    mclient.close_connection()

# FastAPI 建立
app = FastAPI(
    docs_url=DOCS_URL, redoc_url=REDOC_URL, openapi_url=OPENAPI_URL, lifespan=lifespan
)

app.add_middleware(SessionMiddleware, secret_key=sys_conf.session_secret)