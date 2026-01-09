import datetime
from typing import Literal

from pydantic import BaseModel

from backend.src.infrastructure.enums.users.enums import UserTypeEnum

# 
# class TokenAuthResponse(BaseModel):
#     csrf: str
    
class AuthScheme(BaseModel):
    login: str
    password: str
    
class JWTScheme(BaseModel):
    user_id: int
    exp: datetime.datetime