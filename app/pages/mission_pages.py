from typing import Annotated

from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import RedirectResponse
from beanie import PydanticObjectId
from configs import app_conf

from models.mission import Mission, PendingMissionReview
from models.user import User
from shared import WebPage
from shared.dependencies import get_current_user
from shared.time_funcs import get_now
from shared.types import MissionReviewState

router = APIRouter(prefix="/mission", dependencies=[Depends(get_current_user)])


def get_mission_id(mission_obj):
    """Helper function to safely extract mission ID from Link or Mission object"""
    if hasattr(mission_obj, 'fetch'):
        # It's a Link object, we need to access the ref_id
        return str(mission_obj.ref.id) if hasattr(mission_obj.ref, 'id') else None
    else:
        # It's already a Mission object
        return str(mission_obj.id) if hasattr(mission_obj, 'id') else None


def has_user_completed_mission(user, mission_id):
    """Check if user has already completed a specific mission"""
    completed_mission_ids = [get_mission_id(m) for m in user.completed_missions]
    completed_mission_ids = [id for id in completed_mission_ids if id is not None]
    return mission_id in completed_mission_ids


@router.get("/index.html")
@router.get("/")
@WebPage.build().page("mission/mission_board.html", "任務板")
async def mission_index_page(
    request: Request, 
    current_user: Annotated[User, Depends(get_current_user)]
):
    # 獲取所有可用任務（根據當前session和用戶等級過濾）
    available_missions = await Mission.find(
        Mission.session == app_conf.mission,
        Mission.accepted_min_level <= current_user.level,
        Mission.expired_time > get_now()
    ).to_list()
    
    # 獲取用戶當前進行中的任務ID列表
    ongoing_mission_ids = [get_mission_id(mission) for mission in current_user.ongoing_missions]
    ongoing_mission_ids = [id for id in ongoing_mission_ids if id is not None]
    
    # 處理任務資料
    missions_data = []
    for mission in available_missions:
        mission_id = str(mission.id)
        is_accepted = mission_id in ongoing_mission_ids
        has_completed = has_user_completed_mission(current_user, mission_id)
        
        # 檢查該任務是否正在 Review 中
        existing_review_mission = await PendingMissionReview.find_one(
            PendingMissionReview.mission_id == mission_id,
            PendingMissionReview.user_id == str(current_user.id),
            PendingMissionReview.session == app_conf.mission,
            PendingMissionReview.review_status == MissionReviewState.PENDDING,
        )
        
        from shared import console
        console.info(existing_review_mission)
        
        # 檢查是否可以接受任務
        can_accept = (
            not is_accepted and 
            not (not mission.is_repetitive and has_completed) and  # 不可重複且已完成的任務不能再接
            len(current_user.ongoing_missions) < current_user.max_missions and
            current_user.token >= mission.invest and 
            (existing_review_mission is None)
        )
        
        missions_data.append({
            "id": mission_id,
            "name": mission.name,
            "description": mission.description,
            "rewards": mission.rewards,
            "accepted_min_level": mission.accepted_min_level,
            "invest": mission.invest,
            "tags": mission.tags,
            "created_time": mission.created_time,
            "expired_time": mission.expired_time,
            "is_repetitive": mission.is_repetitive,
            "is_accepted": is_accepted,
            "has_completed": has_completed,
            "is_reviewing": (existing_review_mission is not None),
            "can_accept": can_accept
        })
    
    return {
        "missions": missions_data,
        "user": {
            "level": current_user.level,
            "token": current_user.token,
            "ongoing_count": len(current_user.ongoing_missions),
            "max_missions": current_user.max_missions
        }
    }




@router.get("/{mission_id}/detail.html")
@WebPage.build().page("mission/mission_detail.html", "任務詳情")
async def mission_detail_page(
    request: Request,
    mission_id: str,
    current_user: Annotated[User, Depends(get_current_user)]
):
    try:
        mission = await Mission.get(PydanticObjectId(mission_id))
        if not mission or mission.session != app_conf.mission:
            raise HTTPException(status_code=404, detail="任務不存在")
    except Exception:
        raise HTTPException(status_code=404, detail="任務不存在")
    
    # 檢查用戶是否已接受此任務
    ongoing_mission_ids = [get_mission_id(m) for m in current_user.ongoing_missions]
    ongoing_mission_ids = [id for id in ongoing_mission_ids if id is not None]
    is_accepted = mission_id in ongoing_mission_ids
    has_completed = has_user_completed_mission(current_user, mission_id)
    
    # 檢查該任務是否正在 Review 中
    existing_review_mission = await PendingMissionReview.find_one(
        PendingMissionReview.mission_id == mission_id,
        PendingMissionReview.user_id == str(current_user.id),
        PendingMissionReview.session == app_conf.mission,
        PendingMissionReview.review_status == MissionReviewState.PENDDING,
    )
    
    # 檢查是否可以接受
    can_accept = (
        not is_accepted and
        not (not mission.is_repetitive and has_completed) and  # 不可重複且已完成的任務不能再接
        len(current_user.ongoing_missions) < current_user.max_missions and
        current_user.token >= mission.invest and
        current_user.level >= mission.accepted_min_level and
        mission.expired_time > get_now() and
        (existing_review_mission is None)
    )
    
    mission_data = {
        "id": str(mission.id),
        "name": mission.name,
        "description": mission.description,
        "rewards": mission.rewards,
        "accepted_min_level": mission.accepted_min_level,
        "invest": mission.invest,
        "tags": mission.tags,
        "created_time": mission.created_time,
        "expired_time": mission.expired_time,
        "need_upload_proof": mission.need_upload_proof,
        "is_repetitive": mission.is_repetitive,
        "is_accepted": is_accepted,
        "has_completed": has_completed,
        "is_reviewing": (existing_review_mission is not None),
        "can_accept": can_accept
    }
    
    return {
        "mission": mission_data,
        "user": {
            "level": current_user.level,
            "token": current_user.token,
            "ongoing_count": len(current_user.ongoing_missions),
            "max_missions": current_user.max_missions
        }
    }


@router.post("/{mission_id}/accept")
async def mission_accept_action(
    request: Request,
    mission_id: str,
    current_user: Annotated[User, Depends(get_current_user)]
):
    try:
        mission = await Mission.get(PydanticObjectId(mission_id))
        if not mission or mission.session != app_conf.mission:
            request.session["error"] = "任務不存在"
            return RedirectResponse(url=request.url_for("mission_index_page"), status_code=302)
        
        # 檢查任務是否已過期
        if mission.expired_time <= get_now():
            request.session["error"] = "任務已過期"
            return RedirectResponse(url=request.url_for("mission_index_page"), status_code=302)
        
        # 檢查用戶等級
        if current_user.level < mission.accepted_min_level:
            request.session["error"] = f"等級不足，需要等級 {mission.accepted_min_level}"
            return RedirectResponse(url=request.url_for("mission_index_page"), status_code=302)
        
        # 檢查用戶代幣是否足夠
        if current_user.token < mission.invest:
            request.session["error"] = f"代幣不足，需要 {mission.invest} 代幣"
            return RedirectResponse(url=request.url_for("mission_index_page"), status_code=302)
        
        # 檢查任務數量限制
        if len(current_user.ongoing_missions) >= current_user.max_missions:
            request.session["error"] = f"任務數量已達上限 ({current_user.max_missions})"
            return RedirectResponse(url=request.url_for("mission_index_page"), status_code=302)
        
        # 檢查是否已經接受此任務
        ongoing_mission_ids = [get_mission_id(m) for m in current_user.ongoing_missions]
        ongoing_mission_ids = [id for id in ongoing_mission_ids if id is not None]
        if mission_id in ongoing_mission_ids:
            request.session["error"] = "您已經接受了這個任務"
            return RedirectResponse(url=request.url_for("mission_index_page"), status_code=302)
        
        # 檢查不可重複任務是否已完成
        if not mission.is_repetitive and has_user_completed_mission(current_user, mission_id):
            request.session["error"] = "此任務不可重複接取，您已經完成過了"
            return RedirectResponse(url=request.url_for("mission_index_page"), status_code=302)
        
        # 檢查任務是否為完成，還是只是在審核階段；審核階段任務也不可以再重新處理
        wait_for_review_mission = await PendingMissionReview.find_one(
            PendingMissionReview.mission_id == mission_id,
            PendingMissionReview.user_id == str(current_user.id),
            PendingMissionReview.session == app_conf.mission,
            PendingMissionReview.review_status == MissionReviewState.PENDDING,
        )
        
        if wait_for_review_mission:
            request.session["error"] = "此任務尚在審核，還不能接取"
            return RedirectResponse(url=request.url_for("mission_index_page"), status_code=302)
        
        
        # 扣除押金並添加任務
        current_user.token -= mission.invest
        current_user.ongoing_missions.append(mission)
        await current_user.save()
        
        request.session["success"] = f"成功接受任務 '{mission.name}'"
        if mission.invest > 0:
            request.session["success"] += f"，已扣除押金 {mission.invest} 代幣"
        
        return RedirectResponse(url=request.url_for("user_index_page"), status_code=302)
        
    except Exception as e:
        request.session["error"] = f"接受任務失敗: {str(e)}"
        return RedirectResponse(url=request.url_for("mission_index_page"), status_code=302)


@router.post("/{mission_id}/abandon")
async def mission_abandon_action(
    request: Request,
    mission_id: str,
    current_user: Annotated[User, Depends(get_current_user)]
):
    try:
        mission = await Mission.get(PydanticObjectId(mission_id))
        if not mission:
            request.session["error"] = "任務不存在"
            return RedirectResponse(url=request.url_for("user_index_page"), status_code=302)
        
        # 檢查用戶是否有此任務
        mission_found = False
        for i, ongoing_mission in enumerate(current_user.ongoing_missions):
            mission_id_str = get_mission_id(ongoing_mission)
            if mission_id_str == mission_id:
                current_user.ongoing_missions.pop(i)
                mission_found = True
                break
        
        if not mission_found:
            request.session["error"] = "您沒有接受這個任務"
            return RedirectResponse(url=request.url_for("user_index_page"), status_code=302)
        
        await current_user.save()
        
        abandon_msg = f"已放棄任務 '{mission.name}'"
        if mission.invest > 0:
            abandon_msg += f"，押金 {mission.invest} 代幣不予退還"
        
        request.session["success"] = abandon_msg
        return RedirectResponse(url=request.url_for("user_index_page"), status_code=302)
        
    except Exception as e:
        request.session["error"] = f"放棄任務失敗: {str(e)}"
        return RedirectResponse(url=request.url_for("user_index_page"), status_code=302)


@router.post("/{mission_id}/submit")
async def mission_submit_action(
    request: Request,
    mission_id: str,
    current_user: Annotated[User, Depends(get_current_user)]
):
    try:
        mission = await Mission.get(PydanticObjectId(mission_id))
        if not mission:
            request.session["error"] = "任務不存在"
            return RedirectResponse(url=request.url_for("user_index_page"), status_code=302)
        
        # 檢查用戶是否有此任務
        mission_found = False
        for i, ongoing_mission in enumerate(current_user.ongoing_missions):
            mission_id_str = get_mission_id(ongoing_mission)
            if mission_id_str == mission_id:
                current_user.ongoing_missions.pop(i)
                mission_found = True
                break
        
        if not mission_found:
            request.session["error"] = "您沒有接受這個任務"
            return RedirectResponse(url=request.url_for("user_index_page"), status_code=302)
        
        # 檢查是否已經提交過審核
        existing_review = await PendingMissionReview.find_one(
            PendingMissionReview.mission_id == mission_id,
            PendingMissionReview.user_id == str(current_user.id),
            PendingMissionReview.session == app_conf.mission,
            PendingMissionReview.review_status == MissionReviewState.PENDDING,
        )
        
        # 任務存在且為非重複性任務，那就不給予提交
        if existing_review:
            existing_review_mission = await Mission.get(PydanticObjectId(existing_review.mission_id))
            if not existing_review_mission.is_repetitive:
                request.session["error"] = "此任務已提交審核，請等待結果"
                return RedirectResponse(url=request.url_for("user_index_page"), status_code=302)
        
        # 創建審核記錄
        review = PendingMissionReview(
            session=app_conf.mission,
            mission_id=mission_id,
            user_id=str(current_user.id),
            campus_id=current_user.campus_id,
            review_status=MissionReviewState.PENDDING
        )
        
        await review.save()
        
        # 添加到用戶的待審核列表
        current_user.review_pending_missions.append(review)
        await current_user.save()
        
        request.session["success"] = f"任務 '{mission.name}' 已提交審核"
        return RedirectResponse(url=request.url_for("user_index_page"), status_code=302)
        
    except Exception as e:
        request.session["error"] = f"提交任務失敗: {str(e)}"
        return RedirectResponse(url=request.url_for("user_index_page"), status_code=302)


@router.post("/clear-session-messages")
async def clear_session_messages(request: Request):
    # 清除session中的消息
    request.session.pop("success", None)
    request.session.pop("error", None)
    return {"status": "ok"}