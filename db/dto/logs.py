from datetime import datetime
from typing import Literal

from pydantic import BaseModel

from db.dto import SecretDTO


class LogDTO(BaseModel):
    id: int
    secret_id: int
    secret: SecretDTO
    event: Literal["create", "delete"]
    ip: str
    created_at: datetime
