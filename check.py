import asyncio
import datetime

import aiohttp
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from backend.db_connection import SDB_ENGINE
from backend.src.infrastructure.models import User
from backend.src.infrastructure.pydantic_models.users import PyUser
from backend.src.modules.shared.unit_of_work import UnitOfWork


async def main():
    async with aiohttp.ClientSession() as session:


        await asyncio.gather(*[check(session) for i in range(3)])

async def check(session):
    async with session.get('http://localhost:8000/auth/health') as resp:
        print(datetime.datetime.now())

# if __name__ == '__main__':
#     asyncio.run(main())
# 
# async def main():
#     uow = UnitOfWork(async_sessionmaker(SDB_ENGINE, class_=AsyncSession, expire_on_commit=False)())
#     async with uow:
#         print('here')
    

if __name__ == '__main__':
    asyncio.run(main())