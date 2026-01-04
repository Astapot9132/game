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

    def to_pydantic_if_model_exists(self, instance: Row, 
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
                       returning_fields: list[InstrumentedAttribute[Any]] | None = None,
                       commit: bool = False):
        if not value:
            return

        query = insert(self.model).values(**value)
        if returning_fields:
            query = query.returning(*returning_fields)
        executed_query = await self.session.execute(query)
        result = executed_query.fetchone() if returning_fields else None
        if commit:
            await self.session.commit()

        return result
    
    async def add_many(self, values: list[dict], 
                       returning_fields: list[InstrumentedAttribute[Any]]|None = None,
                       commit: bool = False):
        if not values:
            return
        
        query = insert(self.model).values(values)
        if returning_fields:
            query = query.returning(*returning_fields)
        executed_query = await self.session.execute(query)
        result = executed_query.fetchall() if returning_fields else None
        if commit:
            await self.session.commit()
        
        return result
            
    

    @classmethod
    async def add_many_with_ignore_conflict(cls, values: list[dict],
                                              commit: bool = False,
                                              returning_fields: list[InstrumentedAttribute[Any]] = None,
                                              ):
        """
        Метод INSERT IGNORE
        """
        if values:
            query_insert = insert(cls.model).values(values).prefix_with('IGNORE')

            if returning_fields:
                query_insert = query_insert.returning(*returning_fields)

            executed_query = await self.session.execute(query_insert)
            if commit:
                await self.session.commit()

            result = executed_query.fetchall() if returning_fields else None
            return result
    
    
    async def delete_by_id(self, id: int, commit: bool = False):
        query = delete(self.model).where(self.model.id == id)
        await self.session.execute(query)
        if commit:
            await self.session.commit()
        return None