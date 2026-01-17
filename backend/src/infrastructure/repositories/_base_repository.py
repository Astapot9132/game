from abc import ABC
from typing import Any, Type, Literal

from pydantic import BaseModel
from sqlalchemy import select, Row, delete
from sqlalchemy.dialects.mysql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute

from backend.db_mixins import BaseSQLModel
from backend.src.modules.shared.exceptions import RepositoryModelIsNotDefined, PydanticModelIsNotImplemented


class SqlAlchemyRepository(ABC):
    
    model = NotImplemented
    pydantic_model = NotImplemented

    def __init__(self, session: AsyncSession):
        
        self.session = session
        if not hasattr(self, 'model'):
            raise RepositoryModelIsNotDefined(f'Модель для репозитория {self.__class__.__name__} не определена')

    def to_pydantic(self, instance: Row, 
                                    pydantic_not_implemented: Literal['exception', 'return_instance'] = 'return_instance'):
        if self.pydantic_model:
            return self.pydantic_model.model_validate(instance, from_attributes=True)
        if pydantic_not_implemented == 'return_instance':
            return instance
        else:
            raise PydanticModelIsNotImplemented()

    async def get_by_id(self, id: int, select_fields: list[InstrumentedAttribute[Any]] | None = None):
        
        model_fields = select_fields if select_fields else (self.model,)
        query = select(*model_fields).where(self.model.id == id) # type: ignore
        executed_query = await self.session.execute(query)
        result = executed_query.first() if select_fields else executed_query.scalars().first()
        return self.to_pydantic(result) if result else None

    async def add(self, value: dict[str, Any],
                       commit: bool = False):
        if not value:
            return

        query = insert(self.model).values(**value)
        executed_query = await self.session.execute(query)
        if commit:
            await self.session.commit()

        return executed_query.lastrowid
    
    async def add_many(self, values: list[dict],
                       commit: bool = False):
        if not values:
            return
        
        query = insert(self.model).values(values)
        executed_query = await self.session.execute(query)
        result = executed_query.lastrowid
        if commit:
            await self.session.commit()
        
        return result
            
    

    async def add_with_ignore_conflict(self,
                                            value: dict,
                                            commit: bool = False,
                                            ):
        """
        Метод INSERT IGNORE
        """
        if value:
            query_insert = insert(self.model).values(**value).prefix_with('IGNORE')
            executed_query = await self.session.execute(query_insert)
            if commit:
                await self.session.commit()

            return executed_query.lastrowid
    
    
    async def delete_by_id(self, id: int, commit: bool = False):
        query = delete(self.model).where(self.model.id == id)
        await self.session.execute(query)
        if commit:
            await self.session.commit()
        return None