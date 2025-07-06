from typing import Annotated

from configs import app_conf
from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from models.mission import Mission, MissionReviewState, PendingMissionReview

# for type hint
from models.user import User
from shared import WebPage
from shared.dependencies import get_admin_user

router = APIRouter(prefix='/reviews', dependencies=[Depends(get_admin_user)])


def get_mission_id(mission_obj):
    """Helper function to safely extract mission ID from Link or Mission object"""
    if hasattr(mission_obj, 'fetch'):
        # It's a Link object, we need to access the ref_id
        return str(mission_obj.ref.id) if hasattr(mission_obj.ref, 'id') else None
    else:
        # It's already a Mission object
        return str(mission_obj.id) if hasattr(mission_obj, 'id') else None


def get_review_id(review_obj):
    """Helper function to safely extract review ID from Link or PendingMissionReview object"""
    if hasattr(review_obj, 'fetch'):
        # It's a Link object, we need to access the ref_id
        return str(review_obj.ref.id) if hasattr(review_obj.ref, 'id') else None
    else:
        # It's already a PendingMissionReview object
        return str(review_obj.id) if hasattr(review_obj, 'id') else None


@router.get("/index.html")
@router.get("/")
@WebPage.build().page("admin/review_list.html", "任務審核")
async def review_list_page(
    request: Request, admin_user: Annotated[User, Depends(get_admin_user)]
):
    from shared.time_funcs import get_now

    reviews = await PendingMissionReview.find(
        PendingMissionReview.session == app_conf.mission
    ).to_list()

    reviews_data = []
    for review in reviews:
        # Get mission details
        mission = await Mission.get(review.mission_id)
        mission_name = mission.name if mission else "Unknown Mission"

        # Get user details
        user = await User.get(review.user_id)
        user_name = user.name if user else "Unknown User"

        reviews_data.append(
            {
                "id": str(review.id),
                "mission_id": review.mission_id,
                "mission_name": mission_name,
                "user_id": review.user_id,
                "user_name": user_name,
                "campus_id": review.campus_id,
                "submitted_time": review.submitted_time,
                "review_status": review.review_status,
                "reviewer_id": review.reviewer_id,
                "review_time": review.review_time,
                "review_comments": review.review_comments,
            }
        )

    return {"reviews": reviews_data}


@router.get("/{review_id}")
@WebPage.build().page("admin/review_detail.html", "審核詳情")
async def review_detail_page(
    request: Request,
    review_id: str,
    admin_user: Annotated[User, Depends(get_admin_user)],
):
    review = await PendingMissionReview.get(review_id)
    if not review or review.session != app_conf.mission:
        raise HTTPException(status_code=404, detail="Review not found")

    # Get mission details
    mission = await Mission.get(review.mission_id)
    mission_data = None
    if mission:
        mission_data = {
            "id": str(mission.id),
            "name": mission.name,
            "description": mission.description,
            "rewards": mission.rewards,
        }

    # Get user details
    user = await User.get(review.user_id)
    user_data = None
    if user:
        user_data = {
            "id": str(user.id),
            "name": user.name,
            "campus_id": user.campus_id,
            "level": user.level,
        }

    review_data = {
        "id": str(review.id),
        "mission_id": review.mission_id,
        "user_id": review.user_id,
        "campus_id": review.campus_id,
        "submitted_time": review.submitted_time,
        "review_status": review.review_status,
        "reviewer_id": review.reviewer_id,
        "review_time": review.review_time,
        "review_comments": review.review_comments,
    }

    return {"review": review_data, "mission": mission_data, "user": user_data}


@router.post("/{review_id}/approve")
async def review_approve_action(
    request: Request,
    review_id: str,
    admin_user: Annotated[User, Depends(get_admin_user)],
    comments: Annotated[str, Form()] = "",
):
    from shared.time_funcs import get_now

    review = await PendingMissionReview.get(review_id)
    if not review or review.session != app_conf.mission:
        raise HTTPException(status_code=404, detail="Review not found")

    # Update review status
    review.review_status = MissionReviewState.APPROVED
    review.reviewer_id = str(admin_user.id)
    review.review_time = get_now()
    review.review_comments = comments
    await review.save()

    # Move mission to user's completed missions and award tokens
    user = await User.get(review.user_id)
    mission = await Mission.get(review.mission_id)

    if user and mission:
        # Add to completed missions
        if mission not in user.completed_missions:
            user.completed_missions.append(mission)

        # Remove from ongoing missions
        user.ongoing_missions = [
            m for m in user.ongoing_missions if get_mission_id(m) != review.mission_id
        ]

        # Remove from review pending missions
        user.review_pending_missions = [
            r for r in user.review_pending_missions if get_review_id(r) != review_id
        ]

        # Award tokens
        user.token += mission.rewards

        await user.save()

    return RedirectResponse(
        url=request.url_for("review_list_page"), status_code=status.HTTP_303_SEE_OTHER
    )


@router.post("/{review_id}/reject")
async def review_reject_action(
    request: Request,
    review_id: str,
    admin_user: Annotated[User, Depends(get_admin_user)],
    comments: Annotated[str, Form()] = "",
):
    from shared.time_funcs import get_now

    review = await PendingMissionReview.get(review_id)
    if not review or review.session != app_conf.mission:
        raise HTTPException(status_code=404, detail="Review not found")

    # Update review status
    review.review_status = MissionReviewState.REJECTED
    review.reviewer_id = str(admin_user.id)
    review.review_time = get_now()
    review.review_comments = comments
    await review.save()

    # Remove from user's pending reviews but keep mission in ongoing
    user = await User.get(review.user_id)
    if user:
        user.review_pending_missions = [
            r for r in user.review_pending_missions if get_review_id(r) != review_id
        ]
        await user.save()

    return RedirectResponse(
        url=request.url_for("review_list_page"), status_code=status.HTTP_303_SEE_OTHER
    )
