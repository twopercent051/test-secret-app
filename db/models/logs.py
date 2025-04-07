from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.models.secrets import SecretModel
from db.models.base import BaseModel, intpk, str_200, created_at


class LogModel(BaseModel):
    __tablename__ = "logs"

    id: Mapped[intpk]
    secret_id: Mapped[int] = mapped_column(ForeignKey(column=SecretModel.id))
    secret: Mapped[SecretModel] = relationship(argument=SecretModel, foreign_keys=[secret_id])
    event: Mapped[str_200]
    ip: Mapped[str_200]
    created_at: Mapped[created_at]
