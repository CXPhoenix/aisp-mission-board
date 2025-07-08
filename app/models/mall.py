from typing import Annotated, Any, Callable, Optional

from beanie import Document, Indexed, Link
from pydantic import Field, model_validator
from shared.time_funcs import get_now
from shared.types import PhysicalProductRequestStatus, ProductType, Utc8Datetime


class Product(Document):
    name: str
    desc: str = ""
    cost: Annotated[int, Field(..., ge=0, description="0 表示免費商品"), Indexed()]
    stock: Annotated[int, Field(-1, ge=-1, description="-1 表示無限個商品可以購買")]
    update_time: Annotated[Utc8Datetime, Field(default_factory=get_now)]
    level_can_buy: Annotated[
        int, Field(1, ge=1, description="1 為所有人都可以買(最小等級就為 1)")
    ]
    user_can_hold: Annotated[
        int, Field(0, ge=0, description="0 表示玩家可持有無限數量")
    ]
    user_can_use: Annotated[bool, Field(True, description="玩家是否可以使用。有些東西玩家不能使用，如「成就徽章」等")]
    
    # 新增商品類型相關字段
    product_type: Annotated[ProductType, Field(ProductType.STANDARD, description="商品類型")]
    level_increase: Annotated[int, Field(0, ge=0, description="等級提升數量（僅 level_up 類型使用）")]
    auto_use: Annotated[bool, Field(False, description="是否自動使用（購買後立即使用）")]
    is_physical: Annotated[bool, Field(False, description="是否為實體兌換的內容")]

    @model_validator(mode='after')
    def validate_product_settings(self):
        """根據商品類型自動設定相關屬性"""
        # 只有實體物品有這個要求，因此預設為 False，實體物品類別會轉為 True
        self.is_physical = False
        if self.product_type == ProductType.LEVEL_UP:
            # 等級提升道具必須自動使用
            self.auto_use = True
        elif self.product_type == ProductType.PHYSICAL:
            # 實體商品需要配送
            self.is_physical = True
            # 實體商品不自動使用
            self.auto_use = False
        elif self.product_type == ProductType.BADGE:
            # 成就徽章玩家不能使用
            self.user_can_use = False
            self.auto_use = False
        
        return self

    def can_buy(cond_func: Callable[..., bool], **cond_params: Any) -> bool:
        """判斷除了售價、庫存、可買等級及角色可擁有數量等條件外的購買條件。

        這邊我使用了類似於 filter 的做法。

        Args:
            cond_func (Callable[..., bool]): 條件函式，用於判斷條件
            cond_params (dict[str, Any]): cond_func 的參數

        Returns:
            bool: 條件判斷的結果
        """
        return cond_func(**cond_params)

    class Settings:
        name = "products"


class PhysicalProductRequest(Document):
    """實體商品申請記錄
    
    管理實體商品的購買申請、審核、配送等完整流程
    """
    
    product: Link[Product]
    user_campus_id: Annotated[str, Field(..., min_length=1, description="申請用戶的校園ID")]
    
    # 時間記錄
    request_time: Annotated[Utc8Datetime, Field(default_factory=get_now, description="申請時間")]
    approval_time: Annotated[Optional[Utc8Datetime], Field(None, description="審核時間")]
    
    # 狀態與審核
    status: Annotated[PhysicalProductRequestStatus, Field(PhysicalProductRequestStatus.PENDING, description="申請狀態")]
    admin_campus_id: Annotated[Optional[str], Field(None, description="審核管理員的校園ID")]
    admin_notes: Annotated[str, Field("", description="管理員備註")]
    
    
    async def get_user(self):
        """獲取申請用戶對象"""
        from .user import User
        return await User.find(User.campus_id == self.user_campus_id).first_or_none()
    
    async def get_admin_user(self):
        """獲取審核管理員對象"""
        if self.admin_campus_id is None:
            return None
        from .user import User
        return await User.find(User.campus_id == self.admin_campus_id).first_or_none()
    
    
    class Settings:
        name = "physical product requests"
