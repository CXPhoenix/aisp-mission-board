from typing import Annotated

from beanie import Document, Indexed
from pydantic import Field
from shared.time_funcs import get_now, timediff
from shared.types import Utc8Datetime


class Mission(Document):
    name: Annotated[str, Field(..., min_length=1)]
    description: Annotated[str, Field(..., min_length=0)]
    tags: Annotated[list[str], Field([], description="給任務上一些標籤。")]
    rewards: Annotated[
        int, Field(..., ge=0, description="任務完成獎勵 token。預設為 0。")
    ]
    accepted_min_level: Annotated[
        int,
        Field(
            1,
            ge=1,
            description="能接任務的最小等級。預設為 1，表示所有人都能接。(玩家最小等級為 1)",
        ),
        Indexed(),
    ]
    invest: Annotated[
        int,
        Field(
            0,
            ge=0,
            description="需要投注的 token 數。預設為 0，表示不用任何的投注。(類似接任務的押金，沒完成就沒了)",
        ),
    ]
    created_time: Annotated[
        Utc8Datetime, Field(default_factory=get_now, description="任務建立時間。")
    ]
    updated_time: Annotated[
        Utc8Datetime,
        Field(
            default_factory=get_now, description="任務更新時間。這會牽扯到任務版更新。"
        ),
    ]
    expired_time: Annotated[
        Utc8Datetime, Field(defualt=(timediff(36500, unit="days")))
    ]  # 懶得設無限，若沒有過期時限，則設定為 100 年後過期

    class Settings:
        name = "missions"
