from fastapi import APIRouter, Depends, Request, status
from shared import WebPage
from shared.dependencies import get_current_user
from shared.types import Role
from typing import Annotated
from configs import app_conf

# for type hint
from models.user import User, OwnItem
from models.mission import Mission, PendingMissionReview

router = APIRouter(prefix="/user", dependencies=[Depends(get_current_user)])


@router.get("/index.html")
@router.get("/")
@WebPage.build().page("user/user_board.html", "DASHBOARD")
async def user_index_page(request: Request, user: Annotated[User, Depends(get_current_user)]):
    # 取得使用者目前進行的任務
    await user.fetch_all_links()
    
    # 準備任務資料 - 只顯示當前 session 的任務
    ongoing_missions = []
    for mission_link in user.ongoing_missions:
        # Check if it's a Link object or already resolved Mission object
        if hasattr(mission_link, 'fetch'):
            mission = await mission_link.fetch()
        else:
            mission = mission_link
        if mission and mission.session == app_conf.mission:
            ongoing_missions.append({
                "id": str(mission.id),
                "name": mission.name,
                "description": mission.description,
                "rewards": mission.rewards,
                "tags": mission.tags,
                "expired_time": mission.expired_time
            })
    
    # 準備待審核任務資料 - 只顯示當前 session 的任務
    review_pending_missions = []
    for review_link in user.review_pending_missions:
        # Check if it's a Link object or already resolved PendingMissionReview object
        if hasattr(review_link, 'fetch'):
            review = await review_link.fetch()
        else:
            review = review_link
        if review and review.session == app_conf.mission:
            review_pending_missions.append({
                "id": str(review.id),
                "mission_id": review.mission_id,
                "submitted_time": review.submitted_time,
                "review_status": review.review_status
            })
    
    # 準備已完成任務資料 - 只顯示當前 session 的任務
    completed_missions = []
    for mission_link in user.completed_missions:
        # Check if it's a Link object or already resolved Mission object
        if hasattr(mission_link, 'fetch'):
            mission = await mission_link.fetch()
        else:
            mission = mission_link
        if mission and mission.session == app_conf.mission:
            completed_missions.append({
                "id": str(mission.id),
                "name": mission.name,
                "description": mission.description,
                "rewards": mission.rewards,
                "tags": mission.tags
            })
    
    context = {
        "user": {
            "name": user.name,
            "campus_id": user.campus_id,
            "level": user.level,
            "token": user.token,
            "max_missions": user.max_missions,
            "current_missions_count": len(ongoing_missions),
            "roles": user.roles
        },
        "ongoing_missions": ongoing_missions,
        "review_pending_missions": review_pending_missions,
        "completed_missions": completed_missions
    }
    
    return context

@router.get('/bag.html')
@WebPage.build().page("user/user_bag.html", "道具欄")
async def user_bag_page(request: Request, user: Annotated[User, Depends(get_current_user)]):
    # 取得使用者的道具
    await user.fetch_all_links()
    
    # 準備道具資料
    items = []
    for item_link in user.bag:
        # Check if it's a Link object or already resolved OwnItem object
        if hasattr(item_link, 'fetch'):
            own_item = await item_link.fetch()
        else:
            own_item = item_link
        if own_item:
            # Check if item is a Link object or already resolved Product object
            if hasattr(own_item.item, 'fetch'):
                product = await own_item.item.fetch()
            else:
                product = own_item.item
            if product:
                items.append({
                    "id": str(own_item.id),
                    "name": product.name,
                    "description": product.desc,
                    "quantity": own_item.quantity,
                    "user_can_use": own_item.user_can_use,
                    "product_user_can_use": product.user_can_use
                })
    
    context = {
        "user": {
            "name": user.name,
            "campus_id": user.campus_id,
            "level": user.level,
            "token": user.token
        },
        "items": items
    }
    
    return context


@router.post("/clear-session-messages")
async def clear_session_messages(request: Request):
    # 清除session中的消息
    request.session.pop("success", None)
    request.session.pop("error", None)
    return {"status": "ok"}