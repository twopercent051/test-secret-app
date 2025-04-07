from sqlalchemy import select, insert, update

from db.dao.base import BaseDAO, retry_on_disconnect, async_session_maker
from db.dto import SecretDTO
from db.models import SecretModel, LogModel


class SecretsDAO(BaseDAO):
    model = SecretModel

    @classmethod
    @retry_on_disconnect()
    async def get_one_or_none(cls, **filter_by) -> SecretDTO | None:
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(**filter_by).limit(1)
            result = await session.execute(query)
            row = result.scalars().one_or_none()
            if row:
                return SecretDTO.model_validate(obj=row, from_attributes=True)

    @classmethod
    @retry_on_disconnect()
    async def get_many(cls, **filter_by) -> list[SecretDTO]:
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(**filter_by).order_by(cls.model.id)
            data = await session.execute(query)
            return [SecretDTO.model_validate(obj=row, from_attributes=True) for row in data.scalars().all()]

    @classmethod
    @retry_on_disconnect()
    async def create_secret_with_log(cls, encoded_secret: str, encoded_passphrase: str, ttl_seconds: int | None, ip: str) -> SecretDTO:
        async with async_session_maker() as session:
            secret_stmt = insert(cls.model).values(encoded_secret=encoded_secret, encoded_passphrase=encoded_passphrase, ttl_seconds=ttl_seconds).returning(cls.model)
            secret_result = await session.execute(secret_stmt)
            secret_row = secret_result.fetchone()[0]
            log_stmt = insert(LogModel).values(secret_id=secret_row.id, ip=ip, event="create")
            await session.execute(log_stmt)
            await session.commit()
            return SecretDTO.model_validate(obj=secret_row, from_attributes=True)

    @classmethod
    @retry_on_disconnect()
    async def get_secret_with_log(cls, secret_id: int, encoded_passphrase: str,
                                     ip: str) -> SecretDTO | None:
        async with async_session_maker() as session:
            secret_query = select(cls.model).filter_by(id=secret_id, encoded_passphrase=encoded_passphrase).limit(1)
            secret_result = await session.execute(secret_query)
            secret_row = secret_result.fetchone()[0]
            if not secret_row:
                return
            result = SecretDTO.model_validate(obj=secret_row, from_attributes=True)
            secret_stmt = update(cls.model).values(encoded_secret=None).filter_by(id=secret_id)
            log_stmt = insert(LogModel).values(secret_id=secret_id, ip=ip, event="get")
            await session.execute(secret_stmt)
            await session.execute(log_stmt)
            await session.commit()
            return result

    @classmethod
    async def __delete_secret(cls, ip: str, **params) -> bool:
        async with async_session_maker() as session:
            secret_stmt = update(cls.model).values(encoded_secret=None).filter_by(**params).returning(cls.model.id)
            secret_result = await session.execute(secret_stmt)
            secret_row = secret_result.fetchone()  # Получаем строку данных
            if not secret_row:
                return False
            secret_id = secret_row[0]
            log_stmt = insert(LogModel).values(secret_id=secret_id, ip=ip, event="delete")
            await session.execute(log_stmt)
            await session.commit()
            return True

    @classmethod
    @retry_on_disconnect()
    async def delete_secret_with_log(cls, secret_id: int, encoded_passphrase: str, ip: str) -> bool:
        return await cls.__delete_secret(ip=ip, id=secret_id, encoded_passphrase=encoded_passphrase)

    @classmethod
    @retry_on_disconnect()
    async def delete_secret_by_secret_id(cls, secret_id: int) -> bool:
        return await cls.__delete_secret(ip="---", id=secret_id)