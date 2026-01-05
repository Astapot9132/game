from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from backend.src.infrastructure.repositories.user_repository import UserRepository


class UnitOfWork:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repository = UserRepository(self.session)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        return await self.session.__aexit__(exc_type, exc_val, exc_tb)