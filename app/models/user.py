from typing import Annotated, Any

from beanie import BackLink, Document, Indexed, Link
from passlib.context import CryptContext
from pydantic import BeforeValidator, Field
from shared.time_funcs import get_now
from shared.types import Role, Utc8Datetime

from .mall import Product
from .mission import Mission, MissionSubmitted

# Password hashes configurations
passwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def is_valid_bcrypt_hash(s):
    """
    嚴格驗證字串是否符合完整的 bcrypt (MCF) 格式。
    """
    if not isinstance(s, str):
        return False

    parts = s.split("$")

    # 一個有效的 bcrypt 雜湊值分割後應該有 4 個部分:
    # ['', '2b', '12', 'salt_and_hash']
    if len(parts) != 4:
        return False

    identifier = parts[1]
    cost = parts[2]
    salt_and_hash = parts[3]

    # 1. 檢查演算法識別碼
    if identifier not in ("2a", "2b", "2y"):
        return False

    # 2. 檢查成本參數是否為數字
    if not cost.isdigit():
        return False

    # 3. 檢查鹽值與雜湊值的長度是否正確（鹽值 22 + 雜湊 31 = 53）
    if len(salt_and_hash) != 53:
        return False

    # 如果所有檢查都通過，則可視為有效的 bcrypt 雜湊值
    return True


def _get_passwd_hash(plain_passwd: str) -> str:
    if is_valid_bcrypt_hash(plain_passwd):
        return plain_passwd
    return passwd_context.hash(plain_passwd)


HashPasswd = Annotated[str, BeforeValidator(_get_passwd_hash)]


class User(Document):
    """User model

    Args:
        ### 必要項目
        - campus_id (str): 學校學號/員工編號
        - name (str): 姓名
        - password (str): 密碼 (會自動雜湊，若原本就是雜湊值，則會判斷是否為 bcrypt 的雜湊值，沒問題就直接存進去)

        ### 以下為可選
        - roles ('Role'): 角色，預設為 Role.USER
        - disabled (bool): 使用者是否禁用，預設為 False
        - create_time (datetime): 註冊時間，基本上是由管理員匯入。自動處理成 UTC+8 的格式輸出
        - last_signin_time (datetime): 上次登入時間。
        - level (int): 角色等級，目前沒設定上限，我想應該也不用...
        - token (int): 角色代幣
        - badges (list): 還沒設定
        - bag (list): 跟 OwnItem 連動
        - max_missions (int): 任務領取數
        - accepted_missions (list): 跟 Mission 聯動，目前的任務數
    """

    campus_id: Annotated[str, Field(...), Indexed(unique=True)]
    name: Annotated[str, Field(..., min_length=1)]
    password: Annotated[HashPasswd, Field(...)]
    roles: list[Role] = [Role.USER]
    create_time: Annotated[Utc8Datetime, Field(default_factory=get_now)]
    last_signin_time: Annotated[Utc8Datetime, Field(default_factory=get_now)]
    disabled: Annotated[bool, Field(False, description="是否停用")]

    # 以下為使用者遊戲畫的相關資訊
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
    ongoing_missions: Annotated[
        list[Link[Mission]],
        Field(
            [],
            max_length=10,
            description="目前玩家所擁有的任務。可能根據等級會改變。系統中最多存放 10 筆。",
        ),
    ]
    review_pending_missions: Annotated[
        list[Link[MissionSubmitted]], Field([], description="等代審核通過的任務")
    ]
    completed_missions: Annotated[
        list[Link[MissionSubmitted]],
        Field(
            [],
            description="目前玩家所完成的任務。",
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
