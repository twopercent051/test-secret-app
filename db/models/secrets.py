from sqlalchemy.orm import Mapped

from db.models.base import BaseModel, intpk, str_200


class SecretModel(BaseModel):
    __tablename__ = "secrets"

    id: Mapped[intpk]
    encoded_secret: Mapped[str_200 | None]
    encoded_passphrase: Mapped[str_200]
    ttl_seconds: Mapped[int | None]
