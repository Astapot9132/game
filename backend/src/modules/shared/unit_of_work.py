from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.infrastructure.repositories.user_repository import UserRepository


class UnitOfWork:
    def __init__(self, session: AsyncSession):
        
        self.user_repository = UserRepository(session)
        
