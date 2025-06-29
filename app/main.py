import traceback
from contextlib import asynccontextmanager
from typing import Any

from configs import app_conf, sys_conf
from fastapi import FastAPI, Request, status
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from models import OwnItem, Product, TransactionRecord, UseItemRecord, User
from pages import auth_pages, mall_pages, mission_pages, user_pages
from shared import SessionMiddleware, mclient
from shared.types import HTTPExceptionName
from shared.webpage import WebPage
from starlette.exceptions import HTTPException as StarletteHTTPException

# Open API Doc 參數設定
DOCS_URL = None  # default is `/docs`
REDOC_URL = None  # default is `/redoc`
OPENAPI_URL = None  # default is `/openapi.json`


# Server 開始與結束時的事件設定
@asynccontextmanager
async def lifespan(app: FastAPI):
    # TODO: Model Import
    mclient.build_connection()
    await mclient.init_database_connection(app_conf.userdb, [User, OwnItem])
    await mclient.init_database_connection(app_conf.malldb, [Product])
    await mclient.init_database_connection(
        app_conf.recorddb, [TransactionRecord, UseItemRecord]
    )
    yield
    mclient.close_connection()


# FastAPI 建立
app = FastAPI(
    docs_url=DOCS_URL, redoc_url=REDOC_URL, openapi_url=OPENAPI_URL, lifespan=lifespan
)

app.add_middleware(SessionMiddleware, secret_key=sys_conf.session_secret)


@app.exception_handler(StarletteHTTPException)
def custom_http_exception_handler(request: Request, exc):
    exception_name = HTTPExceptionName[f"_{exc.status_code}"].value
    return_page = None
    if isinstance(exc.detail, dict):
        return_page: dict[str, Any] = exc.detail.get("return_page", {})
    exception_desc = f"你所查看的頁面 `<code class='font-bold rounded-lg p-2'>{request.url.path}</code>` 不存在。"
    # TODO: 處理不同 status_code 的 exception_desc
    exception_detail = {
        "exception_title": f"{exc.status_code} {exception_name}",
        # TODO: Development, production mode need to delete.
        "exception_desc": exception_desc,
        "return_page": {
            "url": request.url_for("index_page"),
            "name": "首頁",
        },
    }
    if return_page:
        exception_detail.update(return_page)
    wp = WebPage.build()
    wp_resp = wp(
        "exception.html",
        request,
        context={"detail": exception_detail},
        subtitle=f"{exc.status_code} {exception_name}",
        status_code=exc.status_code,
    )
    return wp_resp


# 為了解決每次都取得舊的 style.css 問題
class StaticFilesNotCache(StaticFiles):
    def is_not_modified(self, response_headers, request_headers):
        return False


app.mount("/public", StaticFilesNotCache(directory="/app/public"), name="public")


@app.get("/index.html")
@app.get("/")
async def index_page(request: Request):
    redirect_resp = RedirectResponse(
        request.url_for("login_page"), status.HTTP_303_SEE_OTHER
    )
    return redirect_resp


app.include_router(auth_pages.router)
app.include_router(mission_pages.router)
app.include_router(mall_pages.router)
app.include_router(user_pages.router)
