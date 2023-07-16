from uuid import UUID

from sqlalchemy import ForeignKey, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db import Base


class UserSocialAuth(Base):
    __tablename__ = "user_social_auth"
    __table_args__ = (
        UniqueConstraint("user_id", "service"),
        UniqueConstraint("service", "sub"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, server_default=text("gen_random_uuid()"))

    user_id: Mapped[UUID] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"), nullable=False)

    service: Mapped[str] = mapped_column(index=True)

    sub: Mapped[str] = mapped_column(index=True)
    name: Mapped[str]
    email: Mapped[str]
    locale: Mapped[str]

    user = relationship("User", lazy="raise")
