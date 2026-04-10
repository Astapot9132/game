import datetime

from pydantic import BaseModel, ConfigDict


class AuthScheme(BaseModel):
    login: str
    password: str
    
class JWTScheme(BaseModel):
    model_config = ConfigDict(extra='forbid')
    
    user_id: int
    exp: datetime.datetime