from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

import settings


async_engine = create_async_engine(
    settings.DATABASE_URL.replace("postgresql:", "postgresql+asyncpg:"),
    pool_pre_ping=True,
    echo=settings.DEBUG and False,
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    autoflush=False,
    future=True,
    expire_on_commit=False,
)

metadata = MetaData(
    naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }
)


def load_models():
    """called from alembic to create migrations"""
    import os

    files = filter(lambda e: not e.startswith("__"), os.listdir(os.path.join(os.path.dirname(__file__), "models")))
    for file in files:
        exec(f"from .models import {os.path.splitext(file)[0]}")
