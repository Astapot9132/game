from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from backend.src.infrastructure.repositories.user_repository import UserRepository


class UnitOfWork:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repository = UserRepository(session)
    