from enum import Enum


class UserLanguageEnum(str, Enum):
    RU = 'RU'
    
class UserTypeEnum(str, Enum):
    admin = 'admin'
    player = 'player'