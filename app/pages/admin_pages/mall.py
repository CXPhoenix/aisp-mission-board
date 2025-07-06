from typing import Annotated

from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from models.mall import Product

# for type hint
from models.user import User
from shared import WebPage
from shared.dependencies import get_admin_user

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
):
    product = Product(
        name=name,
        desc=desc,
        cost=cost,
        stock=stock,
        level_can_buy=level_can_buy,
        user_can_hold=user_can_hold,
        user_can_use=user_can_use,
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

    await product.delete()

    return RedirectResponse(
        url=request.url_for("product_list_page"), status_code=status.HTTP_303_SEE_OTHER
    )
