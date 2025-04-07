import asyncio
from typing import List

from sqlalchemy import insert, update, delete
from sqlalchemy.exc import InterfaceError, OperationalError
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from create_app import DATABASE_URL, logger

engine = create_async_engine(url=DATABASE_URL)

async_session_maker = async_sessionmaker(bind=engine, expire_on_commit=False)


def retry_on_disconnect(max_retries: int = 7, delay: int = 1):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return await func(*args, **kwargs)
                except (InterfaceError, OperationalError) as e:
                    retries += 1
                    error_message = str(e)
                    short_message = error_message.split(":")[-1].strip()
                    error_text = f"Connection error: {short_message}. Retry {retries}/{max_retries}..."
                    logger.warning(msg=error_text)
                    await asyncio.sleep(delay)

        return wrapper

    return decorator


class BaseDAO:
    model = None

    @classmethod
    @retry_on_disconnect()
    async def create_one(cls, **data) -> int:
        async with async_session_maker() as session:
            stmt = insert(cls.model).values(**data).returning(cls.model.id)
            result = await session.execute(stmt)
            created_id = result.scalar()
            await session.commit()
            return created_id

    @classmethod
    @retry_on_disconnect()
    async def create_many(cls, data: List[dict]):
        async with async_session_maker() as session:
            stmt = insert(cls.model).values(data)
            await session.execute(stmt)
            await session.commit()

    @classmethod
    @retry_on_disconnect()
    async def update_by_id(cls, item_id: int, **data):
        async with async_session_maker() as session:
            stmt = update(cls.model).values(**data).filter_by(id=item_id)
            await session.execute(stmt)
            await session.commit()

    @classmethod
    @retry_on_disconnect()
    async def delete(cls, **data):
        async with async_session_maker() as session:
            stmt = delete(cls.model).filter_by(**data)
            await session.execute(stmt)
            await session.commit()

    @classmethod
    @retry_on_disconnect()
    async def delete_many_by_ids(cls, ids: list[int]):
        async with async_session_maker() as session:
            stmt = delete(cls.model).where(cls.model.id.in_(ids))
            await session.execute(stmt)
            await session.commit()