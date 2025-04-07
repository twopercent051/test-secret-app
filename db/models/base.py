from datetime import datetime
from typing import Annotated

from sqlalchemy import MetaData, text
from sqlalchemy.orm import mapped_column, as_declarative

intpk = Annotated[int, mapped_column(primary_key=True)]
str_200 = Annotated[str, 200]
created_at = Annotated[datetime, mapped_column(server_default=text("TIMEZONE('utc', now())"))]


@as_declarative()
class BaseModel:
    metadata = MetaData()