from typing import Annotated

from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from models.mall import Product, PhysicalProductRequest

# for type hint
from models.user import User, OwnItem
from shared import WebPage
from shared.dependencies import get_admin_user
from shared.types import ProductType, PhysicalProductRequestStatus

router = APIRouter(prefix='/products', dependencies=[Depends(get_admin_user)])


@router.get("/index.html")
@router.get("/")
@WebPage.build().page("admin/product_list.html", "商品管理")
async def product_list_page(
    request: Request, admin_user: Annotated[User, Depends(get_admin_user)]
):
    products = await Product.find_all().to_list()

    products_data = []
    for product in products:
        products_data.append(
            {
                "id": str(product.id),
                "name": product.name,
                "desc": product.desc,
                "cost": product.cost,
                "stock": product.stock,
                "level_can_buy": product.level_can_buy,
                "user_can_hold": product.user_can_hold,
                "user_can_use": product.user_can_use,
                "update_time": product.update_time,
                "product_type": product.product_type,
                "level_increase": product.level_increase,
                "auto_use": product.auto_use,
                "is_physical": product.is_physical,
            }
        )

    return {"products": products_data}


@router.get("/create")
@WebPage.build().page("admin/product_form.html", "新增商品")
async def product_create_page(
    request: Request, admin_user: Annotated[User, Depends(get_admin_user)]
):
    return {"mode": "create", "product": None}


@router.post("/create")
async def product_create_action(
    request: Request,
    admin_user: Annotated[User, Depends(get_admin_user)],
    name: Annotated[str, Form()],
    desc: Annotated[str, Form()] = "",
    cost: Annotated[int, Form()] = 0,
    stock: Annotated[int, Form()] = -1,
    level_can_buy: Annotated[int, Form()] = 1,
    user_can_hold: Annotated[int, Form()] = 0,
    user_can_use: Annotated[bool, Form()] = True,
    product_type: Annotated[ProductType, Form()] = ProductType.STANDARD,
    level_increase: Annotated[int, Form()] = 0,
    auto_use: Annotated[bool, Form()] = False,
    is_physical: Annotated[bool, Form()] = False,
):
    product = Product(
        name=name,
        desc=desc,
        cost=cost,
        stock=stock,
        level_can_buy=level_can_buy,
        user_can_hold=user_can_hold,
        user_can_use=user_can_use,
        product_type=product_type,
        level_increase=level_increase,
        auto_use=auto_use,
        is_physical=is_physical,
    )

    await product.save()

    return RedirectResponse(
        url=request.url_for("product_list_page"), status_code=status.HTTP_303_SEE_OTHER
    )


@router.get("/edit/{product_id}")
@WebPage.build().page("admin/product_form.html", "編輯商品")
async def product_edit_page(
    request: Request,
    product_id: str,
    admin_user: Annotated[User, Depends(get_admin_user)],
):
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
        "user_can_use": product.user_can_use,
        "product_type": product.product_type,
        "level_increase": product.level_increase,
        "auto_use": product.auto_use,
        "is_physical": product.is_physical,
    }

    return {"mode": "edit", "product": product_data}


@router.post("/edit/{product_id}")
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
    user_can_use: Annotated[bool, Form()] = True,
    product_type: Annotated[ProductType, Form()] = ProductType.STANDARD,
    level_increase: Annotated[int, Form()] = 0,
    auto_use: Annotated[bool, Form()] = False,
    is_physical: Annotated[bool, Form()] = False,
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
    product.product_type = product_type
    product.level_increase = level_increase
    product.auto_use = auto_use
    product.is_physical = is_physical
    product.update_time = get_now()

    await product.save()

    return RedirectResponse(
        url=request.url_for("product_list_page"), status_code=status.HTTP_303_SEE_OTHER
    )


@router.post("/delete/{product_id}")
async def product_delete_action(
    request: Request,
    product_id: str,
    admin_user: Annotated[User, Depends(get_admin_user)],
):
    product = await Product.get(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Cascade deletion: Clean up all references to this product
    
    # 1. Find all OwnItem documents that reference this product
    own_items = await OwnItem.find(OwnItem.item.id == product.id).to_list()
    
    # 2. Remove these OwnItems from users' bag arrays and delete the OwnItems
    for own_item in own_items:
        # Find the user who owns this item using direct query (BackLink.fetch() doesn't work)
        user = await User.find_one(User.bag.id == own_item.id)
        if user and user.bag:
            # Remove the OwnItem from user's bag
            user.bag = [bag_item for bag_item in user.bag if bag_item.ref.id != own_item.id]
            await user.save()
        
        # Delete the OwnItem document
        await own_item.delete()
    
    # 4. Clean up PhysicalProductRequest entries
    physical_requests = await PhysicalProductRequest.find(PhysicalProductRequest.product.id == product.id).to_list()
    for request_item in physical_requests:
        await request_item.delete()
    
    # 5. Finally delete the product itself
    await product.delete()

    return RedirectResponse(
        url=request.url_for("product_list_page"), status_code=status.HTTP_303_SEE_OTHER
    )


# 實體商品申請管理路由
physical_router = APIRouter(prefix='/physical-requests', dependencies=[Depends(get_admin_user)])


@physical_router.get("/index.html")
@physical_router.get("/")
@WebPage.build().page("admin/physical_product_requests.html", "實體商品申請管理")
async def physical_product_requests_page(
    request: Request, admin_user: Annotated[User, Depends(get_admin_user)]
):
    requests = await PhysicalProductRequest.find_all().to_list()
    
    requests_data = []
    for req in requests:
        user = await req.get_user()
        admin_user_obj = await req.get_admin_user()
        
        requests_data.append({
            "id": str(req.id),
            "product": req.product,
            "user_campus_id": req.user_campus_id,
            "user_name": user.name if user else "未知用戶",
            "request_time": req.request_time,
            "approval_time": req.approval_time,
            "status": req.status.value,
            "admin_campus_id": req.admin_campus_id,
            "admin_name": admin_user_obj.name if admin_user_obj else None,
            "admin_notes": req.admin_notes,
        })
    
    return {
        "requests": requests_data,
        "status_options": [
            {"value": PhysicalProductRequestStatus.PENDING.value, "label": "待審核"},
            {"value": PhysicalProductRequestStatus.APPROVED.value, "label": "已核准"},
            {"value": PhysicalProductRequestStatus.REJECTED.value, "label": "已拒絕"},
            {"value": PhysicalProductRequestStatus.FULFILLED.value, "label": "已完成"},
        ]
    }


@physical_router.post("/update/{request_id}")
async def update_physical_product_request(
    request: Request,
    request_id: str,
    admin_user: Annotated[User, Depends(get_admin_user)],
    state: Annotated[PhysicalProductRequestStatus, Form()],
    admin_notes: Annotated[str, Form()] = "",
):
    from shared.time_funcs import get_now
    
    product_request = await PhysicalProductRequest.get(request_id)
    if not product_request:
        raise HTTPException(status_code=404, detail="Request not found")
    
    product_request.status = state
    product_request.admin_campus_id = admin_user.campus_id
    product_request.admin_notes = admin_notes
    product_request.approval_time = get_now()
    
    await product_request.save()
    
    return RedirectResponse(
        url=request.url_for("physical_product_requests_page"), 
        status_code=status.HTTP_303_SEE_OTHER
    )
