from typing import Annotated, Any, Callable

from beanie import Document, Indexed
from pydantic import Field
from shared.time_funcs import get_now
from shared.types import Utc8Datetime


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
