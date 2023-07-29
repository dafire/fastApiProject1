from datetime import datetime

from pydantic import BaseModel, ConfigDict
from sqlalchemy import UUID, text
from sqlalchemy.orm import Mapped, mapped_column

from db import Base


class User(Base):
    __tablename__ = "user"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, server_default=text("gen_random_uuid()"))

    email: Mapped[str] = mapped_column(unique=True)
    active: Mapped[bool] = mapped_column(server_default=text("true"))

    last_login: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    def __repr__(self):
        return f"<User(email={self.email!r})>"


class CachedUser(BaseModel):
    id: str
    active: bool

    model_config = ConfigDict(from_attributes=True)
    loaded_at: datetime = datetime.utcnow()
