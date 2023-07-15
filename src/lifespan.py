from contextlib import asynccontextmanager

from fastapi import FastAPI

import settings
from utils.jinja2_templates import JinjaTemplates


@asynccontextmanager
async def lifespan(_: FastAPI):
    _settings = settings.get_settings(settings.Settings)

    # Initialize Templates
    JinjaTemplates.initialize(
        template_path=_settings.template_folder,
        static_path=_settings.static_folder,
        auto_reload=_settings.debug,
        debug=_settings.debug,
    )
    # Start Application
    yield
