from typing import Annotated

from beanie import Document, Link
from pydantic import Field
from shared.time_funcs import get_now
from shared.types import Utc8Datetime

from .mall import Product
from .user import OwnItem, User


class TransactionRecord(Document):
    product: Link[Product]
    buyer: Link[User]
    transacted_time: Annotated[Utc8Datetime, Field(default_factory=get_now)]
    token_spending: Annotated[int, Field(..., ge=0)]
    before_tansacting_quantity: Annotated[int, Field(0, ge=0)]
    transacting_quantity: Annotated[int, Field(1, gt=0)]
    after_transacted_quantity: Annotated[int, Field(..., gt=0)]

    class Settings:
        name = "transacting records"


class UseItemRecord(Document):
    own_item: Link[OwnItem]
    user: Link[User]
    used_time: Annotated[Utc8Datetime, Field(default_factory=get_now)]
    before_using_quantity: Annotated[int, Field(..., gt=0)]
    using_quantity: Annotated[int, Field(..., ge=0)]
    after_used_quantity: Annotated[int, Field(..., ge=0)]

    class Settings:
        name = "item using records"


# TODO: Future work
class OperationRecord(Document):
    ...

    class Settings:
        name = "operation records"
