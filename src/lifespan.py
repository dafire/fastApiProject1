from contextlib import asynccontextmanager

from fastapi import FastAPI

from utils.jinja2_templates import JinjaTemplates


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Initialize Templates
    JinjaTemplates.initialize()
    # Start Application
    yield
