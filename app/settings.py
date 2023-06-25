from starlette.config import Config
from starlette.datastructures import Secret, URL

config = Config(env_file=".env")

if DEBUG := config("DEBUG", cast=bool, default=False):
    SECRET_KEY = config("SECRET_KEY", cast=Secret, default="secret")
else:
    SECRET_KEY = config("SECRET_KEY", cast=Secret)

DATABASE_URL = config("DATABASE_URL", cast=str)