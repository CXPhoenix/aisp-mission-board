from typing import Annotated
from datetime import datetime

from configs import app_conf
from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from models.mission import Mission, MissionSubmitted

# for type hint
from models.user import User
from shared import WebPage
from shared.dependencies import get_admin_user
from shared.time_funcs import get_now, taipei_timezone

router = APIRouter(prefix="/missions", dependencies=[Depends(get_admin_user)])


@router.get("/index.html")
@router.get("/")
@WebPage.build().page("admin/mission_list.html", "任務管理")
async def mission_list_page(
    request: Request, admin_user: Annotated[User, Depends(get_admin_user)]
):
    missions = await Mission.find(Mission.session == app_conf.mission).to_list()

    missions_data = []
    for mission in missions:
        missions_data.append(
            {
                "id": str(mission.id),
                "name": mission.name,
                "description": mission.description,
                "rewards": mission.rewards,
                "accepted_min_level": mission.accepted_min_level,
                "invest": mission.invest,
                "tags": mission.tags,
                "created_time": mission.created_time,
                "expired_time": mission.expired_time,
                "is_repetitive": mission.is_repetitive,
                "need_upload_proof": mission.need_upload_proof,
            }
        )

    return {"missions": missions_data}


@router.get("/create.html")
@WebPage.build().page("admin/mission_form.html", "新增任務")
async def mission_create_page(
    request: Request, admin_user: Annotated[User, Depends(get_admin_user)]
):
    return {"mode": "create", "mission": None}


@router.post("/create")
async def mission_create_action(
    request: Request,
    name: Annotated[str, Form()],
    description: Annotated[str, Form()],
    rewards: Annotated[int, Form()],
    accepted_min_level: Annotated[int, Form()] = 1,
    invest: Annotated[int, Form()] = 0,
    tags: Annotated[str, Form()] = "",
    is_repetitive: Annotated[bool, Form()] = False,
    expired_time: Annotated[str, Form()] = "",
    need_upload_proof: Annotated[bool, Form()] = False,
):
    tags_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
    
    # Parse expired_time from datetime-local input
    if expired_time:
        # datetime-local format: "YYYY-MM-DDTHH:MM"
        try:
            naive_dt = datetime.strptime(expired_time, "%Y-%m-%dT%H:%M")
            # Convert to Taiwan timezone (UTC+8)
            parsed_expired_time = naive_dt.replace(tzinfo=taipei_timezone)
        except ValueError:
            # If parsing fails, use default (100 years from now)
            from models.mission import set_inif
            parsed_expired_time = set_inif()
    else:
        # Use default if not provided
        from models.mission import set_inif
        parsed_expired_time = set_inif()

    mission = Mission(
        session=app_conf.mission,
        name=name,
        description=description,
        rewards=rewards,
        accepted_min_level=accepted_min_level,
        invest=invest,
        tags=tags_list,
        is_repetitive=is_repetitive,
        expired_time=parsed_expired_time,
        need_upload_proof=need_upload_proof,
    )

    await mission.save()

    return RedirectResponse(
        url=request.url_for("mission_list_page"), status_code=status.HTTP_303_SEE_OTHER
    )


@router.get("/edit/{mission_id}")
@WebPage.build().page("admin/mission_form.html", "編輯任務")
async def mission_edit_page(
    request: Request,
    mission_id: str,
    admin_user: Annotated[User, Depends(get_admin_user)],
):
    mission = await Mission.get(mission_id)
    if not mission or mission.session != app_conf.mission:
        raise HTTPException(status_code=404, detail="Mission not found")

    # Convert expired_time to HTML datetime-local format
    expired_time_str = ""
    if mission.expired_time:
        # Convert to Taiwan timezone and format for datetime-local input
        taiwan_dt = mission.expired_time.astimezone(taipei_timezone)
        expired_time_str = taiwan_dt.strftime("%Y-%m-%dT%H:%M")
    
    mission_data = {
        "id": str(mission.id),
        "name": mission.name,
        "description": mission.description,
        "rewards": mission.rewards,
        "accepted_min_level": mission.accepted_min_level,
        "invest": mission.invest,
        "tags": ",".join(mission.tags),
        "is_repetitive": mission.is_repetitive,
        "expired_time": expired_time_str,
        "need_upload_proof": mission.need_upload_proof,
    }

    return {"mode": "edit", "mission": mission_data}


@router.post("/edit/{mission_id}")
async def mission_edit_action(
    request: Request,
    mission_id: str,
    admin_user: Annotated[User, Depends(get_admin_user)],
    name: Annotated[str, Form()],
    description: Annotated[str, Form()],
    rewards: Annotated[int, Form()],
    accepted_min_level: Annotated[int, Form()] = 1,
    invest: Annotated[int, Form()] = 0,
    tags: Annotated[str, Form()] = "",
    is_repetitive: Annotated[bool, Form()] = False,
    expired_time: Annotated[str, Form()] = "",
    need_upload_proof: Annotated[bool, Form()] = False,
):
    mission = await Mission.get(mission_id)
    if not mission or mission.session != app_conf.mission:
        raise HTTPException(status_code=404, detail="Mission not found")

    tags_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
    
    # Parse expired_time from datetime-local input
    if expired_time:
        # datetime-local format: "YYYY-MM-DDTHH:MM"
        try:
            naive_dt = datetime.strptime(expired_time, "%Y-%m-%dT%H:%M")
            # Convert to Taiwan timezone (UTC+8)
            parsed_expired_time = naive_dt.replace(tzinfo=taipei_timezone)
        except ValueError:
            # If parsing fails, keep existing value
            parsed_expired_time = mission.expired_time
    else:
        # Keep existing value if not provided
        parsed_expired_time = mission.expired_time

    mission.name = name
    mission.description = description
    mission.rewards = rewards
    mission.accepted_min_level = accepted_min_level
    mission.invest = invest
    mission.tags = tags_list
    mission.is_repetitive = is_repetitive
    mission.expired_time = parsed_expired_time
    mission.need_upload_proof = need_upload_proof

    await mission.save()

    return RedirectResponse(
        url=request.url_for("mission_list_page"), status_code=status.HTTP_303_SEE_OTHER
    )


@router.post("/delete/{mission_id}")
async def mission_delete_action(
    request: Request,
    mission_id: str,
    admin_user: Annotated[User, Depends(get_admin_user)],
):
    mission = await Mission.get(mission_id)
    if not mission or mission.session != app_conf.mission:
        raise HTTPException(status_code=404, detail="Mission not found")

    # Cascade deletion: Clean up all references to this mission
    
    # 1. Find all users who have this mission in their arrays
    users_with_mission = await User.find(
        {"$or": [
            {"ongoing_missions": {"$elemMatch": {"$id": mission.id}}},
            {"completed_missions": {"$elemMatch": {"$id": mission.id}}}
        ]}
    ).to_list()
    
    # 2. Remove mission from users' ongoing_missions and completed_missions arrays
    for user in users_with_mission:
        updated = False
        
        # Remove from ongoing_missions
        if user.ongoing_missions:
            original_count = len(user.ongoing_missions)
            user.ongoing_missions = [m for m in user.ongoing_missions if m.ref.id != mission.id]
            if len(user.ongoing_missions) != original_count:
                updated = True
        
        # Remove from completed_missions
        if user.completed_missions:
            original_count = len(user.completed_missions)
            user.completed_missions = [m for m in user.completed_missions if m.ref.id != mission.id]
            if len(user.completed_missions) != original_count:
                updated = True
        
        if updated:
            await user.save()
    
    # 3. Clean up related MissionSubmitted entries
    pending_reviews = await MissionSubmitted.find(MissionSubmitted.mission_id == str(mission.id)).to_list()
    for review in pending_reviews:
        # Also remove from users' review_pending_missions arrays
        users_with_review = await User.find(
            {"review_pending_missions": {"$elemMatch": {"$id": review.id}}}
        ).to_list()
        
        for user in users_with_review:
            if user.review_pending_missions:
                user.review_pending_missions = [r for r in user.review_pending_missions if r.ref.id != review.id]
                await user.save()
        
        await review.delete()
    
    # 4. Finally delete the mission itself
    await mission.delete()

    return RedirectResponse(
        url=request.url_for("mission_list_page"), status_code=status.HTTP_303_SEE_OTHER
    )
