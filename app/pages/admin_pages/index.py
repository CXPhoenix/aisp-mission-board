from typing import Annotated

from configs import app_conf
from fastapi import APIRouter, Depends, Request
from models.mall import Product
from models.mission import Mission, MissionSubmitted
from shared.types import MissionReviewState

# for type hint
from models.user import User
from shared import WebPage
from shared.dependencies import get_admin_user

router = APIRouter(dependencies=[Depends(get_admin_user)])

@router.get("/index.html")
@router.get("/")
@WebPage.build().page("admin/admin_board.html", "管理者介面")
async def admin_index_page(
    request: Request, admin_user: Annotated[User, Depends(get_admin_user)]
):
    # 統計資料
    total_missions = await Mission.find(Mission.session == app_conf.mission).count()
    pending_reviews = await MissionSubmitted.find(
        MissionSubmitted.session == app_conf.mission,
        MissionSubmitted.review_status == MissionReviewState.PENDDING,
    ).count()
    total_products = await Product.find_all().count()

    context = {
        "admin_user": {
            "name": admin_user.name,
            "campus_id": admin_user.campus_id,
            "roles": admin_user.roles,
        },
        "stats": {
            "total_missions": total_missions,
            "pending_reviews": pending_reviews,
            "total_products": total_products,
        },
    }

    return context
