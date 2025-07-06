from fastapi import APIRouter, Request, Depends, Form, HTTPException, status
from fastapi.responses import RedirectResponse
from shared import WebPage
from shared.dependencies import get_admin_user
from typing import Annotated
from configs import app_conf

# for type hint
from models.user import User
from models.mission import Mission, PendingMissionReview, MissionReviewState
from models.mall import Product

router = APIRouter(
    prefix="/management",
    dependencies=[Depends(get_admin_user)]
)


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
@WebPage.build().page("admin/admin_board.html", "管理者介面")
async def admin_index_page(request: Request, admin_user: Annotated[User, Depends(get_admin_user)]):
    # 統計資料
    total_missions = await Mission.find(Mission.session == app_conf.mission).count()
    pending_reviews = await PendingMissionReview.find(
        PendingMissionReview.session == app_conf.mission,
        PendingMissionReview.review_status == MissionReviewState.PENDDING
    ).count()
    total_products = await Product.find_all().count()
    
    context = {
        "admin_user": {
            "name": admin_user.name,
            "campus_id": admin_user.campus_id,
            "roles": admin_user.roles
        },
        "stats": {
            "total_missions": total_missions,
            "pending_reviews": pending_reviews,
            "total_products": total_products
        }
    }
    
    return context


# Mission Management
@router.get("/missions.html")
@WebPage.build().page("admin/mission_list.html", "任務管理")
async def mission_list_page(request: Request, admin_user: Annotated[User, Depends(get_admin_user)]):
    missions = await Mission.find(Mission.session == app_conf.mission).to_list()
    
    missions_data = []
    for mission in missions:
        missions_data.append({
            "id": str(mission.id),
            "name": mission.name,
            "description": mission.description,
            "rewards": mission.rewards,
            "accepted_min_level": mission.accepted_min_level,
            "invest": mission.invest,
            "tags": mission.tags,
            "created_time": mission.created_time,
            "expired_time": mission.expired_time,
            "need_upload_proof": mission.need_upload_proof
        })
    
    return {"missions": missions_data}


@router.get("/missions/create.html")
@WebPage.build().page("admin/mission_form.html", "新增任務")
async def mission_create_page(request: Request, admin_user: Annotated[User, Depends(get_admin_user)]):
    return {"mode": "create", "mission": None}


@router.post("/missions/create")
async def mission_create_action(
    request: Request,
    name: Annotated[str, Form()],
    description: Annotated[str, Form()],
    rewards: Annotated[int, Form()],
    accepted_min_level: Annotated[int, Form()] = 1,
    invest: Annotated[int, Form()] = 0,
    tags: Annotated[str, Form()] = "",
    need_upload_proof: Annotated[bool, Form()] = False
):
    tags_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
    
    mission = Mission(
        session=app_conf.mission,
        name=name,
        description=description,
        rewards=rewards,
        accepted_min_level=accepted_min_level,
        invest=invest,
        tags=tags_list,
        need_upload_proof=need_upload_proof
    )
    
    await mission.save()
    
    return RedirectResponse(
        url=request.url_for("mission_list_page"), 
        status_code=status.HTTP_303_SEE_OTHER
    )


@router.get("/missions/edit/{mission_id}")
@WebPage.build().page("admin/mission_form.html", "編輯任務")
async def mission_edit_page(request: Request, mission_id: str, admin_user: Annotated[User, Depends(get_admin_user)]):
    mission = await Mission.get(mission_id)
    if not mission or mission.session != app_conf.mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    
    mission_data = {
        "id": str(mission.id),
        "name": mission.name,
        "description": mission.description,
        "rewards": mission.rewards,
        "accepted_min_level": mission.accepted_min_level,
        "invest": mission.invest,
        "tags": ",".join(mission.tags),
        "need_upload_proof": mission.need_upload_proof
    }
    
    return {"mode": "edit", "mission": mission_data}


@router.post("/missions/edit/{mission_id}")
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
    need_upload_proof: Annotated[bool, Form()] = False
):
    mission = await Mission.get(mission_id)
    if not mission or mission.session != app_conf.mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    
    tags_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
    
    mission.name = name
    mission.description = description
    mission.rewards = rewards
    mission.accepted_min_level = accepted_min_level
    mission.invest = invest
    mission.tags = tags_list
    mission.need_upload_proof = need_upload_proof
    
    await mission.save()
    
    return RedirectResponse(
        url=request.url_for("mission_list_page"), 
        status_code=status.HTTP_303_SEE_OTHER
    )


@router.post("/missions/delete/{mission_id}")
async def mission_delete_action(
    request: Request,
    mission_id: str,
    admin_user: Annotated[User, Depends(get_admin_user)]
):
    mission = await Mission.get(mission_id)
    if not mission or mission.session != app_conf.mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    
    await mission.delete()
    
    return RedirectResponse(
        url=request.url_for("mission_list_page"), 
        status_code=status.HTTP_303_SEE_OTHER
    )


# Mission Review Management
@router.get("/reviews.html")
@WebPage.build().page("admin/review_list.html", "任務審核")
async def review_list_page(request: Request, admin_user: Annotated[User, Depends(get_admin_user)]):
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
        
        reviews_data.append({
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
            "review_comments": review.review_comments
        })
    
    return {"reviews": reviews_data}


@router.get("/reviews/{review_id}")
@WebPage.build().page("admin/review_detail.html", "審核詳情")
async def review_detail_page(request: Request, review_id: str, admin_user: Annotated[User, Depends(get_admin_user)]):
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
            "rewards": mission.rewards
        }
    
    # Get user details
    user = await User.get(review.user_id)
    user_data = None
    if user:
        user_data = {
            "id": str(user.id),
            "name": user.name,
            "campus_id": user.campus_id,
            "level": user.level
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
        "review_comments": review.review_comments
    }
    
    return {
        "review": review_data,
        "mission": mission_data,
        "user": user_data
    }


@router.post("/reviews/{review_id}/approve")
async def review_approve_action(
    request: Request,
    review_id: str,
    admin_user: Annotated[User, Depends(get_admin_user)],
    comments: Annotated[str, Form()] = ""
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
        user.ongoing_missions = [m for m in user.ongoing_missions if get_mission_id(m) != review.mission_id]
        
        # Remove from review pending missions
        user.review_pending_missions = [r for r in user.review_pending_missions if get_review_id(r) != review_id]
        
        # Award tokens
        user.token += mission.rewards
        
        await user.save()
    
    return RedirectResponse(
        url=request.url_for("review_list_page"), 
        status_code=status.HTTP_303_SEE_OTHER
    )


@router.post("/reviews/{review_id}/reject")
async def review_reject_action(
    request: Request,
    review_id: str,
    admin_user: Annotated[User, Depends(get_admin_user)],
    comments: Annotated[str, Form()] = ""
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
        user.review_pending_missions = [r for r in user.review_pending_missions if get_review_id(r) != review_id]
        await user.save()
    
    return RedirectResponse(
        url=request.url_for("review_list_page"), 
        status_code=status.HTTP_303_SEE_OTHER
    )


# Product Management
@router.get("/products.html")
@WebPage.build().page("admin/product_list.html", "商品管理")
async def product_list_page(request: Request, admin_user: Annotated[User, Depends(get_admin_user)]):
    products = await Product.find_all().to_list()
    
    products_data = []
    for product in products:
        products_data.append({
            "id": str(product.id),
            "name": product.name,
            "desc": product.desc,
            "cost": product.cost,
            "stock": product.stock,
            "level_can_buy": product.level_can_buy,
            "user_can_hold": product.user_can_hold,
            "user_can_use": product.user_can_use,
            "update_time": product.update_time
        })
    
    return {"products": products_data}


@router.get("/products/create")
@WebPage.build().page("admin/product_form.html", "新增商品")
async def product_create_page(request: Request, admin_user: Annotated[User, Depends(get_admin_user)]):
    return {"mode": "create", "product": None}


@router.post("/products/create")
async def product_create_action(
    request: Request,
    admin_user: Annotated[User, Depends(get_admin_user)],
    name: Annotated[str, Form()],
    desc: Annotated[str, Form()] = "",
    cost: Annotated[int, Form()] = 0,
    stock: Annotated[int, Form()] = -1,
    level_can_buy: Annotated[int, Form()] = 1,
    user_can_hold: Annotated[int, Form()] = 0,
    user_can_use: Annotated[bool, Form()] = True
):
    product = Product(
        name=name,
        desc=desc,
        cost=cost,
        stock=stock,
        level_can_buy=level_can_buy,
        user_can_hold=user_can_hold,
        user_can_use=user_can_use
    )
    
    await product.save()
    
    return RedirectResponse(
        url=request.url_for("product_list_page"), 
        status_code=status.HTTP_303_SEE_OTHER
    )


@router.get("/products/edit/{product_id}")
@WebPage.build().page("admin/product_form.html", "編輯商品")
async def product_edit_page(request: Request, product_id: str, admin_user: Annotated[User, Depends(get_admin_user)]):
    product = await Product.get(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    product_data = {
        "id": str(product.id),
        "name": product.name,
        "desc": product.desc,
        "cost": product.cost,
        "stock": product.stock,
        "level_can_buy": product.level_can_buy,
        "user_can_hold": product.user_can_hold,
        "user_can_use": product.user_can_use
    }
    
    return {"mode": "edit", "product": product_data}


@router.post("/products/edit/{product_id}")
async def product_edit_action(
    request: Request,
    product_id: str,
    admin_user: Annotated[User, Depends(get_admin_user)],
    name: Annotated[str, Form()],
    desc: Annotated[str, Form()] = "",
    cost: Annotated[int, Form()] = 0,
    stock: Annotated[int, Form()] = -1,
    level_can_buy: Annotated[int, Form()] = 1,
    user_can_hold: Annotated[int, Form()] = 0,
    user_can_use: Annotated[bool, Form()] = True
):
    from shared.time_funcs import get_now
    
    product = await Product.get(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    product.name = name
    product.desc = desc
    product.cost = cost
    product.stock = stock
    product.level_can_buy = level_can_buy
    product.user_can_hold = user_can_hold
    product.user_can_use = user_can_use
    product.update_time = get_now()
    
    await product.save()
    
    return RedirectResponse(
        url=request.url_for("product_list_page"), 
        status_code=status.HTTP_303_SEE_OTHER
    )


@router.post("/products/delete/{product_id}")
async def product_delete_action(
    request: Request,
    product_id: str,
    admin_user: Annotated[User, Depends(get_admin_user)]
):
    product = await Product.get(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    await product.delete()
    
    return RedirectResponse(
        url=request.url_for("product_list_page"), 
        status_code=status.HTTP_303_SEE_OTHER
    )
