from sqlalchemy import String, BigInteger, SmallInteger, UniqueConstraint
from sqlalchemy.orm import mapped_column, Mapped

from backend.db_mixins import HistoricalMixin, BaseModel
from backend.src.infrastructure.enums.users.enums import UserLanguageEnum, UserTypeEnum


class User(BaseModel, HistoricalMixin):
    __tablename__ = 'users'
    
    id: Mapped[int] = mapped_column(BigInteger(), primary_key=True)
    login: Mapped[str] = mapped_column(String(32))
    password_hash: Mapped[str] = mapped_column(String(255))
    email: Mapped[str|None] = mapped_column(String(255), nullable=True)
    surname: Mapped[str|None] = mapped_column(String(64), nullable=True)
    firstname: Mapped[str|None] = mapped_column(String(64), nullable=True)
    patronymic: Mapped[str|None] = mapped_column(String(64), nullable=True)
    age: Mapped[int|None] = mapped_column(SmallInteger(), nullable=True)
    language: Mapped[UserLanguageEnum] = mapped_column(String(32), server_default='RU')
    type_: Mapped[UserTypeEnum] = mapped_column(String(32), name='type')
    
    
    __table_args__ = (
        UniqueConstraint('login', name='uq_users_login'),
    )
    
    