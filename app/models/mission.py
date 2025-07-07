from typing import Annotated
from datetime import datetime

from beanie import Document, Indexed
from configs import app_conf
from pydantic import Field
from shared.time_funcs import get_now, timediff
from shared.types import MissionReviewState, Utc8Datetime


def set_inif() -> datetime:
    # 設定為 100 年
    return timediff(36500, "days")


class Mission(Document):
    session: Annotated[
        str,
        Field(
            app_conf,
            description="所屬的任務時期（用於假性刪除）；系統紀錄用，不做更動；根據 `app_conf.mission` 會進行 filter",
        ),
        Indexed()
    ]
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
        Utc8Datetime,
        Field(
            default_factory=set_inif,
            description="任務結束時間。懶得設無限，若沒有過期時限，則設定為 100 年後過期",
        ),
    ]  # 懶得設無限，若沒有過期時限，則設定為 100 年後過期
    is_repetitive: Annotated[
        bool, Field(False, description="是否為可以重複接的任務；預設為否")
    ]
    need_upload_proof: Annotated[
        bool, Field(False, description="是否需要上傳完成證明；功能暫時不開放")
    ]


class MissionSubmitted(Document):
    session: Annotated[
        str,
        Field(
            app_conf,
            description="所屬的任務時期（用於假性刪除）；系統紀錄用，不做更動；根據 `app_conf.mission` 會進行 filter",
        ),
        Indexed()
    ]
    mission_id: Annotated[str, Field(..., description="任務 ID")]
    user_id: Annotated[str, Field(..., description="用戶 ID")]
    campus_id: Annotated[str, Field(..., description="校園 ID")]
    completion_proof: Annotated[
        bytes, Field(b"", description="完成證明或說明；功能暫時不開放")
    ]
    submitted_time: Annotated[
        Utc8Datetime, Field(default_factory=get_now, description="提交審核時間")
    ]
    review_status: Annotated[
        MissionReviewState,
        Field(
            MissionReviewState.PENDDING,
            description="審核狀態: pending(等待審核), approved(通過), rejected(拒絕)",
        ),
    ]
    reviewer_id: Annotated[str | None, Field(None, description="審核者 ID")]
    review_time: Annotated[Utc8Datetime | None, Field(None, description="審核時間")]
    review_comments: Annotated[str, Field("", description="審核意見")]

    async def get_mission(self) -> Mission | None:
        return await Mission.get(self.mission_id)
    
    class Settings:
        name = "mission submitted"
