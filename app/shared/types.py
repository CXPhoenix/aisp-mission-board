from datetime import datetime
from enum import Enum, IntEnum
from typing import Annotated

from pydantic import BaseModel, BeforeValidator, ConfigDict

from .time_funcs import format_datetime_to_taipei_dt

# Datetime timezone format
Utc8Datetime = Annotated[datetime, BeforeValidator(format_datetime_to_taipei_dt)]


# For user role's wrapping
class Role(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user"


class HTTPExceptionName(str, Enum):
    _400 = "Bad Request"
    _401 = "Unauthorized"
    _403 = "Forbidden"
    _404 = "Not Found"
    _405 = "Method Not Allowed"
    _406 = "Not Acceptable"
    _408 = "Request Timeout"
    _500 = "Internal Server Error"
    _501 = "Not Implemented"
    _502 = "Bad Gateway"
    _503 = "Service Unavailable"
    _504 = "Gateway Timeout"


class SessionStatus(IntEnum):
    NORMAL = 0
    LOGIN_FAILED = 1


class UserSessionData(BaseModel):
    model_config = ConfigDict(extra="ignore")

    campus_id: str
    name: str
    level: int
    token: int
