from os import PathLike
from pathlib import Path
from typing import Any, Callable, Awaitable
import time

from fastapi import Request, HTTPException, status
from fastapi.responses import Response
from fastapi.templating import Jinja2Templates
from jinja2 import pass_context

from functools import wraps
from .logs import console

import inspect
from configs import app_conf

ROOT_DIR = Path(__file__).parent.parent
TEMPLATE_DEFAULT_DIR = ROOT_DIR / "templates"


@pass_context
def urlx_for(
    context: dict,
    name: str,
    **path_params: Any,
) -> str:
    request: Request = context["request"]
    http_url = request.url_for(name, **path_params)
    if scheme := request.headers.get("x-forwarded-proto"):
        return http_url.replace(scheme=scheme)
    return http_url


@pass_context
def ws_for(
    context: dict,
    name: str,
    **path_params: Any,
) -> str:
    # TODO: 看看要不要特別設定與 websocket 的相連的連結路徑 function
    ...

class WebPage:
    def __init__(
        self,
        template_directory: Path | PathLike | str = TEMPLATE_DEFAULT_DIR,
        **pre_context: Any,
    ):
        self._template = Jinja2Templates(template_directory)
        self._template.env.globals["url_for"] = urlx_for
        self._pre_context = pre_context
        self._webpage_context = {"title": app_conf.title}

    @classmethod
    def build(
        cls,
        template_directory: Path | PathLike | str = TEMPLATE_DEFAULT_DIR,
        **pre_context: Any,
    ) -> "WebPage":
        return cls(template_directory, **pre_context)

    # decorator
    def page(
        self, template_file: PathLike | str, page_subtitle: str | None = None, status: int = status.HTTP_200_OK
    ) -> Awaitable:
        def decorator(func: Callable | Awaitable):
            @wraps(func)
            async def wrap(**kargs):
                request: Request = kargs.get("request")
                if request is None:
                    raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR)
                context: dict[str, Any] = func(**kargs)
                if inspect.isawaitable(context):
                    context = await context
                if isinstance(context, Response):
                    return context
                if page_subtitle:
                    self._webpage_context.update({"subtitle": page_subtitle})
                if not isinstance(context, dict):
                    raise HTTPException(
                        status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail={
                            "error_msgs": [
                                "套用到 @Webpage().page() 的函式，必須回傳 dict。",
                                f"function name: {func.__name__}",
                                f"info: {func.__code__}",
                            ]
                        },
                    )

                context.update({"request": request, "webpage": self._webpage_context, "css_timestamp": str(int(time.time()))})
                context.update(self._pre_context)
                wp_response = self._template.TemplateResponse(
                    name=template_file, context=context, status_code=status
                )
                return wp_response

            return wrap

        return decorator

    def __call__(self, template_file: PathLike | str, request: Request, context: dict[str, Any] = {}, **kargs):
        if kargs.get('subtitle'):
            self._webpage_context.update(subtitle=kargs.get('subtitle'))
        context.update({'request': request, "webpage": self._webpage_context, "css_timestamp": str(int(time.time()))})
        context.update(self._pre_context)
        wp_response = self._template.TemplateResponse(name=template_file, context=context)
        if kargs.get('status_code') and isinstance(kargs.get('status_code'), int):
            wp_response.status_code = kargs.get('status_code')
        if kargs.get('headers') and isinstance(kargs.get('headers'), dict):
            wp_response.headers.update(kargs.get('headers'))
        return wp_response