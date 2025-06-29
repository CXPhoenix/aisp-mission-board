from fastapi import APIRouter, Depends, Request, status
from shared import WebPage
from shared.dependencies import get_current_user

router = APIRouter(prefix="/mission", dependencies=[Depends(get_current_user)])


@router.get("/index.html")
@router.get("/")
@WebPage.build().page("mission_board.html", "MISSION BOARD")
async def mission_index_page(request: Request):
    # TODO: Render board index page
    ...
    return {}
