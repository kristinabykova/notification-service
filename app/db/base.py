from datetime import datetime
from typing import Annotated
import uuid

from sqlalchemy import func, text
from sqlalchemy.orm import DeclarativeBase, mapped_column

pk_uuid = Annotated[
    uuid.UUID, mapped_column(primary_key=True, server_default=func.gen_random_uuid())
]
created_time = Annotated[
    datetime, mapped_column(server_default=text("TIMEZONE('utc', now())"))
]
updated_time = Annotated[
    datetime, mapped_column(server_default=text("TIMEZONE('utc', now())"))
]


class Base(DeclarativeBase): ...
