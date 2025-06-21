from fastapi import FastAPI
from contextlib import asynccontextmanager
from shared.odm import MongoDbClient

DOCS_URL=None # default is `/docs`
REDOC_URL=None # default is `/redoc`
OPENAPI_URL=None # default is `/openapi.json`

@asynccontextmanager
async def lifespan(app: FastAPI):
    # TODO: Database connect
    mclient = MongoDbClient()
    yield
    # TODO: Database connection close
    mclient.close_connection()

app = FastAPI(
    docs_url=DOCS_URL,
    redoc_url=REDOC_URL,
    openapi_url=OPENAPI_URL,
    lifespan=lifespan
)