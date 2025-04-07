from pydantic import BaseModel, Field


class SetSecretSchema(BaseModel):
    secret: str
    passphrase: str
    ttl_seconds: int = Field(default=None, gt=0, description="Time-to-live in seconds, must be greater than 0")


class GetSecretKeySchema(BaseModel):
    secret_key: int


class GetSecretSchema(BaseModel):
    secret: str


class DeleteSecretSchema(BaseModel):
    status: str
