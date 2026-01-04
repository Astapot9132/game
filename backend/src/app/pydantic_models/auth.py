from typing import Literal

from pydantic import BaseModel

from backend.src.infrastructure.enums.users.enums import UserTypeEnum


class TokenAuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    type: Literal['bearer']
    
class AuthScheme(BaseModel):
    login: str
    password: str
    
