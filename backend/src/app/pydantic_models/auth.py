from typing import Literal

from pydantic import BaseModel


class TokenAuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    type: Literal['bearer']
    
class LoginScheme(BaseModel):
    login: str
    password: str