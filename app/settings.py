import os

from starlette.config import Config
from starlette.datastructures import Secret

config = Config(env_file=".env")

DEBUG = config("DEBUG", cast=bool, default=False)

SECRET_KEY = config("SECRET_KEY", cast=Secret)

DATABASE_PASSWORD = config("DATABASE_PASSWORD", cast=Secret, default="")

DATABASE_URL = config(
    "DATABASE_URL",
    default=f"postgresql://postgres:{DATABASE_PASSWORD}@localhost:5434/postgres",
)

STATIC_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "static"))

TEMPLATE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "templates"))
