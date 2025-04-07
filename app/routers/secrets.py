from datetime import datetime, timedelta

import pytz
from fastapi import APIRouter, Depends, HTTPException

from app.dependencies import get_client_ip
from app.schemas.secrets import SetSecretSchema, GetSecretKeySchema, GetSecretSchema, DeleteSecretSchema
from db.dao import SecretsDAO
from utils.crypto import encrypt_passphrase, encrypt_secret, decrypt_secret
from utils.scheduler_utils import create_task

router = APIRouter(prefix="/secrets")


@router.post(path="/")
async def create_secret_endpoint(secret: SetSecretSchema, ip: str = Depends(get_client_ip)) -> GetSecretKeySchema:
    encrypted_passphrase = encrypt_passphrase(passphrase=secret.passphrase)
    encrypted_secret = encrypt_secret(secret=secret.secret)
    created_secret = await SecretsDAO.create_secret_with_log(
        encoded_secret=encrypted_secret, encoded_passphrase=encrypted_passphrase, ttl_seconds=secret.ttl_seconds, ip=ip
    )
    if secret.ttl_seconds:
        run_date = datetime.now(tz=pytz.UTC).replace(tzinfo=None) + timedelta(seconds=secret.ttl_seconds)
        await create_task(secret_id=created_secret.id, run_date=run_date)
    return GetSecretKeySchema(secret_key=created_secret.id)


@router.post(path="/{secret_key}")
async def get_secret_endpoint(secret_key: int, passphrase: str, ip: str = Depends(get_client_ip)) -> GetSecretSchema:
    encrypted_passphrase = encrypt_passphrase(passphrase=passphrase)
    secret = await SecretsDAO.get_secret_with_log(secret_id=secret_key, encoded_passphrase=encrypted_passphrase, ip=ip)
    if not secret or not secret.encoded_secret:
        raise HTTPException(status_code=404, detail="Secret not found")
    decrypted_secret = decrypt_secret(encrypted_secret=secret.encoded_secret)
    return GetSecretSchema(secret=decrypted_secret)


@router.delete(path="/{secret_key}")
async def delete_secret_endpoint(
    secret_key: int, passphrase: str, ip: str = Depends(get_client_ip)
) -> DeleteSecretSchema:
    encrypted_passphrase = encrypt_passphrase(passphrase=passphrase)
    is_deleted = await SecretsDAO.delete_secret_with_log(
        secret_id=secret_key, encoded_passphrase=encrypted_passphrase, ip=ip
    )
    if not is_deleted:
        raise HTTPException(status_code=404, detail="Secret not found")
    return DeleteSecretSchema(status="secret_deleted")
