from orjson import orjson
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from settings import DatabaseSettings, get_settings

_settings = get_settings(DatabaseSettings)


def orjson_serializer(obj):
    return orjson.dumps(obj, option=orjson.OPT_NAIVE_UTC).decode()


async_engine = create_async_engine(
    _settings.url,
    pool_size=20,
    pool_pre_ping=True,
    pool_use_lifo=True,
    echo=_settings.echo,
    json_serializer=orjson_serializer,
)

async_session_factory = async_sessionmaker(bind=async_engine, expire_on_commit=False)
