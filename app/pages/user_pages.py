from fastapi import APIRouter, Depends, Request, status, Form
from fastapi.responses import RedirectResponse
from shared import WebPage
from shared.dependencies import get_current_user
from shared.types import Role, MissionReviewState
from shared.link_utils import safe_fetch_link, safe_fetch_links
from typing import Annotated
from configs import app_conf

# for type hint
from models.user import User, OwnItem
from models.mission import Mission, MissionSubmitted

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
        mission = await safe_fetch_link(mission_link)
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
        review = await safe_fetch_link(review_link)
        if review and review.session == app_conf.mission:
            review_pending_missions.append({
                "id": str(review.id),
                "mission_id": review.mission_id,
                "submitted_time": review.submitted_time,
                "review_status": review.review_status
            })
    
    # 準備已完成任務資料 - 只顯示當前 session 的任務
    completed_missions = []
    ## 重新調整邏輯，使用 MissionSubmitted 去搜尋（雖然慢一點，但是先穩妥）
    mission_submitted_filter = (
        MissionSubmitted.session == app_conf.mission,
        MissionSubmitted.user_id == str(user.id),
        MissionSubmitted.review_status == MissionReviewState.APPROVED,
    )
    for mission_submitted in (await MissionSubmitted.find(*mission_submitted_filter).to_list()):
        mission = await (mission_submitted.get_mission())
        completed_missions.append({
            "id": str(mission_submitted.id),
            "name": mission.name,
            "description": mission.description,
            "rewards": mission.rewards,
            "tags": mission.tags,
        })
    
    ## 備用邏輯
    # for mission_link in user.completed_missions:
    #     mission = await safe_fetch_link(mission_link)
    #     if mission and mission.session == app_conf.mission:
    #         completed_missions.append({
    #             "id": str(mission.id),
    #             "name": mission.name,
    #             "description": mission.description,
    #             "rewards": mission.rewards,
    #             "tags": mission.tags
    #         })
    
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
        own_item = await safe_fetch_link(item_link)
        if own_item:
            product = await safe_fetch_link(own_item.item)
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


@router.post("/item/{item_id}/use")
async def user_use_item(
    request: Request,
    item_id: str,
    user: Annotated[User, Depends(get_current_user)]
):
    from beanie import PydanticObjectId
    from fastapi.responses import RedirectResponse
    
    try:
        # 獲取物品
        own_item = await OwnItem.get(PydanticObjectId(item_id))
        if not own_item:
            request.session["error"] = "物品不存在"
            return RedirectResponse(url=request.url_for("user_bag_page"), status_code=302)
        
        # 檢查物品是否屬於該用戶
        await user.fetch_all_links()
        user_owns_item = False
        for item_link in user.bag:
            user_item = await safe_fetch_link(item_link)
            if user_item and str(user_item.id) == str(own_item.id):
                user_owns_item = True
                break
        
        if not user_owns_item:
            request.session["error"] = "您沒有這個物品"
            return RedirectResponse(url=request.url_for("user_bag_page"), status_code=302)
        
        # 檢查物品是否可以使用
        if not own_item.user_can_use:
            request.session["error"] = "此物品無法使用"
            return RedirectResponse(url=request.url_for("user_bag_page"), status_code=302)
        
        # 獲取產品信息
        product = await safe_fetch_link(own_item.item)
        
        if not product:
            request.session["error"] = "物品信息錯誤"
            return RedirectResponse(url=request.url_for("user_bag_page"), status_code=302)
        
        # 檢查產品是否允許用戶使用
        if not product.user_can_use:
            request.session["error"] = "此商品無法使用"
            return RedirectResponse(url=request.url_for("user_bag_page"), status_code=302)
        
        # 檢查數量
        if own_item.quantity <= 0:
            request.session["error"] = "物品數量不足"
            return RedirectResponse(url=request.url_for("user_bag_page"), status_code=302)
        
        # 根據商品類型執行使用邏輯
        from shared.types import ProductType
        
        if product.product_type == ProductType.LEVEL_UP:
            # 等級提升道具
            user.level += product.level_increase
            success_msg = f"使用 '{product.name}' 成功，等級提升至 {user.level}"
            
        elif product.product_type == ProductType.PHYSICAL:
            # 實體商品：創建申請記錄
            from models.mall import PhysicalProductRequest
            from shared.types import PhysicalProductRequestStatus
            
            physical_request = PhysicalProductRequest(
                product=product,
                user_campus_id=user.campus_id,
                status=PhysicalProductRequestStatus.PENDING
            )
            await physical_request.save()
            success_msg = f"已提交 '{product.name}' 實體商品申請，等待管理員審核"
            
        elif product.product_type == ProductType.BADGE:
            # 徽章不能使用
            request.session["error"] = "成就徽章無法使用，僅作收藏"
            return RedirectResponse(url=request.url_for("user_bag_page"), status_code=302)
            
        else:
            # 標準商品 - 這裡可以根據需要添加具體的使用邏輯
            # 目前只是簡單的消耗物品
            success_msg = f"使用 '{product.name}' 成功"
        
        # 減少物品數量
        own_item.quantity -= 1
        
        # 如果數量為0，從背包中移除
        if own_item.quantity <= 0:
            # 從用戶背包中移除
            for i, item_link in enumerate(user.bag):
                user_item = await safe_fetch_link(item_link)
                if user_item and str(user_item.id) == str(own_item.id):
                    user.bag.pop(i)
                    break
            
            # 刪除物品記錄
            await own_item.delete()
        else:
            # 保存更新的數量
            await own_item.save()
        
        # 保存用戶更新
        await user.save()
        
        request.session["success"] = success_msg
        return RedirectResponse(url=request.url_for("user_bag_page"), status_code=302)
        
    except Exception as e:
        request.session["error"] = f"使用物品失敗: {str(e)}"
        return RedirectResponse(url=request.url_for("user_bag_page"), status_code=302)


@router.post("/clear-session-messages")
async def clear_session_messages(request: Request):
    # 清除session中的消息
    request.session.pop("success", None)
    request.session.pop("error", None)
    return {"status": "ok"}


@router.get("/change-password.html")
@WebPage.build().page("user/change_password.html", "修改密碼")
async def change_password_page(request: Request, user: Annotated[User, Depends(get_current_user)]):
    context = {
        "user": {
            "name": user.name,
            "campus_id": user.campus_id
        }
    }
    return context


@router.post("/change-password")
async def change_password(
    request: Request,
    current_password: Annotated[str, Form()],
    new_password: Annotated[str, Form()],
    confirm_password: Annotated[str, Form()],
    user: Annotated[User, Depends(get_current_user)]
):
    try:
        # 驗證當前密碼是否正確
        if not user.verify_passwd(current_password):
            request.session["error"] = "當前密碼不正確"
            return RedirectResponse(url=request.url_for("change_password_page"), status_code=302)
        
        # 驗證新密碼與確認密碼是否一致
        if new_password != confirm_password:
            request.session["error"] = "新密碼與確認密碼不一致"
            return RedirectResponse(url=request.url_for("change_password_page"), status_code=302)
        
        # 驗證新密碼強度（至少 8 字符）
        if len(new_password) < 8:
            request.session["error"] = "新密碼至少需要 8 個字符"
            return RedirectResponse(url=request.url_for("change_password_page"), status_code=302)
        
        # 檢查新密碼是否與當前密碼相同
        if user.verify_passwd(new_password):
            request.session["error"] = "新密碼不能與當前密碼相同"
            return RedirectResponse(url=request.url_for("change_password_page"), status_code=302)
        
        # 更新用戶密碼
        user.password = new_password  # 會自動透過 HashPasswd 進行雜湊
        await user.save()
        
        request.session["success"] = "密碼修改成功"
        return RedirectResponse(url=request.url_for("user_index_page"), status_code=302)
        
    except Exception as e:
        request.session["error"] = f"密碼修改失敗: {str(e)}"
        return RedirectResponse(url=request.url_for("change_password_page"), status_code=302)