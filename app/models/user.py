from typing import Annotated, Any

from beanie import BackLink, Document, Indexed, Link
from passlib.context import CryptContext
from pydantic import BeforeValidator, Field
from shared.time_funcs import get_now
from shared.types import Role, Utc8Datetime

from .mall import Product
from .mission import Mission

# Password hashes configurations
passwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _get_passwd_hash(plain_passwd: str) -> str:
    return passwd_context.hash(plain_passwd)


HashPasswd = Annotated[str, BeforeValidator(_get_passwd_hash)]


class User(Document):
    campus_id: Annotated[str, Field(...), Indexed(unique=True)]
    name: Annotated[str, Field(..., min_length=1)]
    password: Annotated[HashPasswd, Field(...)]
    roles: list[Role] = [Role.USER]
    create_time: Annotated[Utc8Datetime, Field(default_factory=get_now)]
    last_signin_time: Annotated[Utc8Datetime, Field(default_factory=get_now)]
    level: Annotated[int, Field(1, description="等級", ge=1)]
    token: Annotated[int, Field(0, description="用於商城、升級", ge=0)]
    badges: Annotated[
        list[Any],
        Field([], description="成就系統；尚未啟動", deprecated=True),
    ]
    bag: Annotated[list[Link["OwnItem"]], Field([], description="持有物品")]
    max_missions: Annotated[
        int,
        Field(1, ge=1, le=10, description="玩家可同時領取的任務數。可能根據等級改變。"),
    ]
    accepted_missions: Annotated[
        list[Link[Mission]],
        Field(
            [],
            max_length=10,
            description="目前玩家所擁有的任務。可能根據等級會改變。系統中最多存放 10 筆。",
        ),
    ]

    def verify_passwd(self, plain_passwd) -> bool:
        return passwd_context.verify(plain_passwd, self.password)

    def update_roles(self, role: Role):
        self.roles.append(role)

    def update_last_signin_time(self):
        self.last_signin_time = get_now()

    def check_mission_count_valid(self) -> bool:
        return len(self.accepted_missions) <= self.max_missions

    class Settings:
        name = "users"


class OwnItem(Document):
    owner: BackLink[User] = Field(..., original_field="bag")
    item: Link[Product]
    quantity: Annotated[int, Field(..., gt=0)]
    user_can_use: Annotated[
        bool,
        Field(
            True, description="玩家是否可以使用。有些東西玩家不能使用，如「成就徽章」等"
        ),
    ]

    def add_item(self, count: int = 1):
        self.quantity += count

    class Settings:
        name = "user own items"
