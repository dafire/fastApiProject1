from datetime import datetime

from sqlalchemy import DateTime, MetaData
from sqlalchemy.orm import DeclarativeBase, registry

meta = MetaData(
    naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }
)


class Base(DeclarativeBase):
    __abstract__ = True
    metadata = meta

    registry = registry(
        type_annotation_map={
            datetime: DateTime(timezone=True),
        },
    )

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
