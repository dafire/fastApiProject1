from sqlalchemy import UUID, text
from sqlalchemy.orm import Mapped, mapped_column

from db import Base


class User(Base):
    __tablename__ = "user"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, server_default=text("gen_random_uuid()"))

    email: Mapped[str] = mapped_column(unique=True)
    active: Mapped[bool] = mapped_column(server_default=text("true"))

    def __repr__(self):
        return f"<User(email={self.email!r})>"
