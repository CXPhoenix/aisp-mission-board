from typing import Annotated
from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import RedirectResponse
from beanie import PydanticObjectId

from models.mall import Product, PhysicalProductRequest
from models.user import User, OwnItem
from shared import WebPage
from shared.dependencies import get_current_user
from shared.time_funcs import get_now
from shared.types import ProductType, PhysicalProductRequestStatus
from shared.link_utils import safe_fetch_link

router = APIRouter(prefix="/mall", dependencies=[Depends(get_current_user)])


async def get_user_owned_quantity(user: User, product_id: str) -> int:
    """Get the quantity of a specific product owned by the user"""
    total_quantity = 0
    for item_link in user.bag:
        own_item = await safe_fetch_link(item_link)
        if own_item:
            product = await safe_fetch_link(own_item.item)
            if product and str(product.id) == product_id:
                total_quantity += own_item.quantity
    return total_quantity


@router.get("/index.html")
@router.get("/")
@WebPage.build().page("mall/mall_board.html", "商城")
async def mall_index_page(
    request: Request,
    current_user: Annotated[User, Depends(get_current_user)]
):
    # 獲取所有可用商品
    products = await Product.find().to_list()
    
    # 準備商品資料
    products_data = []
    for product in products:
        # 檢查用戶是否可以購買
        can_buy = (
            current_user.level >= product.level_can_buy and
            current_user.token >= product.cost and
            (product.stock == -1 or product.stock > 0)  # -1 表示無限庫存
        )
        
        # 檢查用戶持有數量限制
        if product.user_can_hold > 0:
            # 計算用戶當前持有數量
            await current_user.fetch_all_links()
            user_owned_count = await get_user_owned_quantity(current_user, str(product.id))
            
            if user_owned_count >= product.user_can_hold:
                can_buy = False
        
        products_data.append({
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
            "can_buy": can_buy,
            "update_time": product.update_time
        })
    
    return {
        "products": products_data,
        "user": {
            "level": current_user.level,
            "token": current_user.token,
            "name": current_user.name
        }
    }


@router.get("/{product_id}/detail.html")
@WebPage.build().page("mall/mall_detail.html", "商品詳情")
async def mall_detail_page(
    request: Request,
    product_id: str,
    current_user: Annotated[User, Depends(get_current_user)]
):
    try:
        product = await Product.get(PydanticObjectId(product_id))
        if not product:
            raise HTTPException(status_code=404, detail="商品不存在")
    except Exception:
        raise HTTPException(status_code=404, detail="商品不存在")
    
    # 檢查用戶是否可以購買
    can_buy = (
        current_user.level >= product.level_can_buy and
        current_user.token >= product.cost and
        (product.stock == -1 or product.stock > 0)
    )
    
    # 檢查用戶持有數量限制
    user_owned_count = 0
    if product.user_can_hold > 0:
        await current_user.fetch_all_links()
        user_owned_count = await get_user_owned_quantity(current_user, str(product.id))
        
        if user_owned_count >= product.user_can_hold:
            can_buy = False
    
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
        "can_buy": can_buy,
        "user_owned_count": user_owned_count,
        "update_time": product.update_time
    }
    
    return {
        "product": product_data,
        "user": {
            "level": current_user.level,
            "token": current_user.token,
            "name": current_user.name
        }
    }


@router.post("/{product_id}/buy")
async def mall_buy_product(
    request: Request,
    product_id: str,
    current_user: Annotated[User, Depends(get_current_user)]
):
    try:
        product = await Product.get(PydanticObjectId(product_id))
        if not product:
            request.session["error"] = "商品不存在"
            return RedirectResponse(url=request.url_for("mall_index_page"), status_code=302)
        
        # 檢查用戶等級
        if current_user.level < product.level_can_buy:
            request.session["error"] = f"等級不足，需要等級 {product.level_can_buy}"
            return RedirectResponse(url=request.url_for("mall_index_page"), status_code=302)
        
        # 檢查用戶代幣
        if current_user.token < product.cost:
            request.session["error"] = f"代幣不足，需要 {product.cost} 代幣"
            return RedirectResponse(url=request.url_for("mall_index_page"), status_code=302)
        
        # 檢查庫存
        if product.stock == 0:
            request.session["error"] = "商品已售完"
            return RedirectResponse(url=request.url_for("mall_index_page"), status_code=302)
        
        # 檢查用戶持有數量限制
        if product.user_can_hold > 0:
            await current_user.fetch_all_links()
            user_owned_count = await get_user_owned_quantity(current_user, str(product.id))
            
            if user_owned_count >= product.user_can_hold:
                request.session["error"] = f"持有數量已達上限 ({product.user_can_hold})"
                return RedirectResponse(url=request.url_for("mall_index_page"), status_code=302)
        
        # 扣除代幣
        current_user.token -= product.cost
        
        # 更新庫存
        if product.stock > 0:
            product.stock -= 1
            await product.save()
        
        # 根據商品類型處理
        if product.product_type == ProductType.PHYSICAL:
            # 實體商品：創建申請記錄
            physical_request = PhysicalProductRequest(
                product=product,
                user_campus_id=current_user.campus_id,
                status=PhysicalProductRequestStatus.PENDING
            )
            await physical_request.save()
            
            await current_user.save()
            request.session["success"] = f"已成功購買 '{product.name}'，實體商品申請已提交，等待管理員審核"
            
        elif product.product_type == ProductType.LEVEL_UP:
            # 等級提升道具：自動使用
            current_user.level += product.level_increase
            
            await current_user.save()
            request.session["success"] = f"已成功購買並使用 '{product.name}'，等級提升至 {current_user.level}"
            
        else:
            # 標準商品或徽章：加入背包
            # 檢查是否已有該商品
            existing_item = None
            for item_link in current_user.bag:
                own_item = await safe_fetch_link(item_link)
                if own_item:
                    item_product = await safe_fetch_link(own_item.item)
                    if item_product and str(item_product.id) == str(product.id):
                        existing_item = own_item
                        break
            
            if existing_item:
                # 增加數量
                existing_item.quantity += 1
                await existing_item.save()
            else:
                # 創建新的擁有物品
                own_item = OwnItem(
                    item=product,
                    quantity=1,
                    user_can_use=product.user_can_use
                )
                await own_item.save()
                current_user.bag.append(own_item)
            
            await current_user.save()
            request.session["success"] = f"已成功購買 '{product.name}' 並加入背包"
        
        return RedirectResponse(url=request.url_for("mall_index_page"), status_code=302)
        
    except Exception as e:
        request.session["error"] = f"購買失敗: {str(e)}"
        return RedirectResponse(url=request.url_for("mall_index_page"), status_code=302)


@router.get("/physical-requests.html")
@WebPage.build().page("mall/mall_physical_requests.html", "實體商品申請")
async def mall_physical_requests_page(
    request: Request,
    current_user: Annotated[User, Depends(get_current_user)]
):
    # 獲取用戶的實體商品申請記錄
    requests = await PhysicalProductRequest.find(
        PhysicalProductRequest.user_campus_id == current_user.campus_id
    ).sort(-PhysicalProductRequest.request_time).to_list()
    
    # 準備申請資料
    requests_data = []
    for req in requests:
        # 獲取商品信息
        product = await safe_fetch_link(req.product)
        
        # 獲取管理員信息
        admin_user = await req.get_admin_user()
        
        requests_data.append({
            "id": str(req.id),
            "product_name": product.name if product else "未知商品",
            "request_time": req.request_time,
            "approval_time": req.approval_time,
            "status": req.status,
            "admin_name": admin_user.name if admin_user else None,
            "admin_notes": req.admin_notes
        })
    
    return {
        "requests": requests_data,
        "user": {
            "name": current_user.name,
            "campus_id": current_user.campus_id
        }
    }


@router.post("/clear-session-messages")
async def clear_session_messages(request: Request):
    # 清除session中的消息
    request.session.pop("success", None)
    request.session.pop("error", None)
    return {"status": "ok"}
