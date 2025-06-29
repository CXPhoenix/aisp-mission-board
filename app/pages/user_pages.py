from fastapi import APIRouter, Depends, Request, status
from shared import WebPage
from shared.dependencies import get_current_user
from typing import Annotated

# for type hint
from models.user import User, OwnItem

router = APIRouter(prefix="/user", dependencies=[Depends(get_current_user)])


@router.get("/index.html")
@router.get("/")
@WebPage.build().page("user_board.html", "MALL")
async def user_index_page(request: Request, user: Annotated[User, Depends(get_current_user)]):
    # TODO: Render board index page
    ...
    return {}
