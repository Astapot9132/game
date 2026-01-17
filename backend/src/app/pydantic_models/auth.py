import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict

from backend.src.infrastructure.enums.users.enums import UserTypeEnum


class AuthScheme(BaseModel):
    login: str
    password: str
    
class JWTScheme(BaseModel):
    model_config = ConfigDict(extra='forbid')
    
    user_id: int
    exp: datetime.datetime