from starlette.config import Config
from starlette.datastructures import Secret, URL

config = Config(env_file=".env")

DEBUG = config("DEBUG", cast=bool, default=False)

SECRET_KEY = config("SECRET_KEY", cast=Secret)

DATABASE_PASSWORD = config("DATABASE_PASSWORD", cast=Secret)

DATABASE_URL = config("DATABASE_URL",  default=f"postgresql://postgres:{DATABASE_PASSWORD}@localhost/postgres")