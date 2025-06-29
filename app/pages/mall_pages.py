from fastapi import APIRouter, Depends, Request, status
from shared import WebPage
from shared.dependencies import get_current_user

router = APIRouter(prefix="/mall", dependencies=[Depends(get_current_user)])


@router.get("/index.html")
@router.get("/")
@WebPage.build().page("mall_board.html", "MALL")
async def mall_index_page(request: Request):
    # TODO: Render board index page
    ...
    return {}
