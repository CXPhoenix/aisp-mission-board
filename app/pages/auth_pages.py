from typing import Annotated

from fastapi import APIRouter, Form, Request, status
from fastapi.responses import RedirectResponse
from models.user import User
from shared import WebPage
from shared.time_funcs import get_now
from shared.types import SessionStatus, UserSessionData

# 登入失敗訊息
LOGIN_FAILED_MSG = "帳號密碼不正確"

router = APIRouter(prefix="/auth")


@router.get("/login.html")
@WebPage.build().page("login.html", "登入")
async def login_page(request: Request):
    context = {}
    status = SessionStatus(request.session.get("status", 0))
    if status == SessionStatus.LOGIN_FAILED:
        context.update({"error_msg": request.session.get("msg", "帳號密碼錯誤")})
    return context


@router.post("/login/", response_class=RedirectResponse)
async def login(
    request: Request, username: Annotated[str, Form()], password: Annotated[str, Form()]
):
    user = await User.find_one(User.name == username)

    # 確認使用者是否存在
    if user is None:
        request.session["status"] = SessionStatus.LOGIN_FAILED
        request.session["msg"] = LOGIN_FAILED_MSG
        return RedirectResponse(
            request.url_for("login_page"), status_code=status.HTTP_303_SEE_OTHER
        )

    # 確認使用者密碼是否正確
    if not user.verify_passwd(password):
        request.session["status"] = SessionStatus.LOGIN_FAILED
        request.session["msg"] = LOGIN_FAILED_MSG
        return RedirectResponse(
            request.url_for("login_page"), status_code=status.HTTP_303_SEE_OTHER
        )

    # 更新使用者上次登入時間紀錄
    user.last_signin_time = get_now()
    await user.save()

    # 更新使用者 session 資訊
    request.session.update(UserSessionData(**user.model_dump()).model_dump())
    return RedirectResponse(
        request.url_for("mission_board_page"), status_code=status.HTTP_303_SEE_OTHER
    )


@router.get("/logout/", response_class=RedirectResponse)
async def logout(request: Request):
    request.session.clear()
    redirect_resp = RedirectResponse(
        request.url_for("index_page"), status.HTTP_303_SEE_OTHER
    )
    return redirect_resp
