from datetime import timedelta
from typing import Literal, Optional

import jwt
from fastapi import FastAPI
from fastapi.requests import HTTPConnection
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from starlette.datastructures import MutableHeaders
from starlette.types import Message, Receive, Scope, Send

from .time_funcs import get_now


class SessionMiddleware:
    def __init__(
        self,
        app: FastAPI,
        secret_key: str,
        session_cookie: str = "session",
        max_age: Optional[int] = 24 * 60 * 60,  # 1 days in default, unit: second
        path: str = "/",
        same_site: Literal["lax", "strict", "none"] = "lax",
        session_struct: type = dict,
    ) -> None:
        self._app = app
        self._secret_key = secret_key
        self._session_cookie = session_cookie
        self._max_age = max_age
        self._path = path
        self.security_flags = "httponly; samesite=" + same_site
        self._session_struct = session_struct

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] not in ("http", "websocket"):  # pragma: no cover
            await self._app(scope, receive, send)
            return

        connection = HTTPConnection(scope)
        initial_session_was_empty = True

        if self._session_cookie in connection.cookies:
            jwt_token = connection.cookies[self._session_cookie].encode("utf-8")
            try:
                data = jwt.decode(jwt_token, self._secret_key, ["HS256"])
                if self._session_struct is not dict:
                    data = self._session_struct(**data)
                scope["session"] = data
                initial_session_was_empty = False
            except InvalidTokenError:
                scope["session"] = {}
            except ExpiredSignatureError:
                scope["session"] = {}
        else:
            scope["session"] = {}

        async def send_wrapper(message: Message) -> None:
            if message["type"] == "http.response.start":
                if scope["session"]:
                    # We have session data to persist.
                    if hasattr(scope["session"], "model_dump"):
                        session_data = scope["session"].model_dump()
                    else:
                        session_data = dict(scope["session"])
                    if "exp" not in session_data:
                        now = get_now()
                        now += timedelta(seconds=self._max_age)
                        scope["session"]["exp"] = now
                    data = jwt.encode(session_data, self._secret_key, "HS256")
                    headers = MutableHeaders(scope=message)
                    header_value = "{session_cookie}={data}; path={path}; {max_age}{security_flags}".format(
                        session_cookie=self._session_cookie,
                        data=data,
                        path=self._path,
                        max_age=f"Max-Age={self._max_age}; " if self._max_age else "",
                        security_flags=self.security_flags,
                    )
                    headers.append("Set-Cookie", header_value)
                elif not initial_session_was_empty:
                    # The session has been cleared.
                    headers = MutableHeaders(scope=message)
                    header_value = "{session_cookie}={data}; path={path}; {expires}{security_flags}".format(
                        session_cookie=self._session_cookie,
                        data="null",
                        path=self._path,
                        expires="expires=Thu, 01 Jan 1970 00:00:00 GMT; ",
                        security_flags=self.security_flags,
                    )
                    headers.append("Set-Cookie", header_value)
            await send(message)

        await self._app(scope, receive, send_wrapper)
