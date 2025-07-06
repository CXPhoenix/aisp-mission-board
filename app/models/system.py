from beanie import Document
from typing import Annotated
from pydantic import Field
from configs import app_conf

class MissionInfo(Document):
    now_mission_session: Annotated[str, Field(app_conf.mission, description="設定目前的 mission session")]
    
    class Settings:
        name = "mission system information"