from pydantic import BaseModel


class SecretDTO(BaseModel):
    id: int
    encoded_secret: str | None
    encoded_passphrase: str
    ttl_seconds: int | None