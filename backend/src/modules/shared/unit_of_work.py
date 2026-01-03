from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from backend.src.infrastructure.repositories._base_repository import SqlAlchemyRepository
from backend.src.infrastructure.repositories.user_repository import UserRepository


class UnitOfWork:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repository = UserRepository
        
    async def __aenter__(self):
        async with self.session as session:
            for attr_name, value in self.__dict__.items():
                if isinstance(value, type) and issubclass(value, SqlAlchemyRepository):
                    setattr(self, attr_name, value(session))
            return self
                
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        print('Закрыли сессию')