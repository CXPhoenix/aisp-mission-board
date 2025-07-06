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
    if (user_campus_id := request.session.get("campus_id")) is not None:
        if (
            await User.find(User.campus_id == user_campus_id).first_or_none()
        ) is not None:
            return RedirectResponse(
                request.url_for("user_index_page"),
                status_code=status.HTTP_303_SEE_OTHER,
            )
    if request.session.get("counting", 0) > 1:
        request.session.pop("counting", None)
        request.session.pop("status", None)
        request.session.pop("msg", None)
    elif request.session.get("counting", 0) == 1:
        request.session["counting"] += 1
    context = {}
    states = SessionStatus(request.session.get("status", 0))
    if states == SessionStatus.LOGIN_FAILED:
        context.update({"error_msg": request.session.get("msg", "帳號密碼錯誤")})
    return context


@router.post("/login/", response_class=RedirectResponse)
async def login(
    request: Request,
    campus_id: Annotated[str, Form()],
    password: Annotated[str, Form()],
):
    user = await User.find_one(User.campus_id == campus_id)

    # 確認使用者是否存在
    if user is None:
        request.session["status"] = SessionStatus.LOGIN_FAILED
        request.session["msg"] = LOGIN_FAILED_MSG
        request.session["counting"] = 1
        return RedirectResponse(
            request.url_for("login_page"), status_code=status.HTTP_303_SEE_OTHER
        )

    # 確認使用者密碼是否正確
    if not user.verify_passwd(password):
        request.session["status"] = SessionStatus.LOGIN_FAILED
        request.session["msg"] = LOGIN_FAILED_MSG
        request.session["counting"] = 1
        return RedirectResponse(
            request.url_for("login_page"), status_code=status.HTTP_303_SEE_OTHER
        )

    # 更新使用者上次登入時間紀錄
    user.update_last_signin_time()
    await user.save()

    # 更新使用者 session 資訊
    request.session.pop("status", None)
    request.session.pop("msg", None)
    request.session.pop("counting", None)
    request.session.update(UserSessionData(**user.model_dump()).model_dump())
    return RedirectResponse(
        request.url_for("user_index_page"), status_code=status.HTTP_303_SEE_OTHER
    )


@router.get("/logout/", response_class=RedirectResponse)
async def logout(request: Request):
    request.session.clear()
    redirect_resp = RedirectResponse(
        request.url_for("index_page"), status.HTTP_303_SEE_OTHER
    )
    return redirect_resp
