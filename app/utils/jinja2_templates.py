import os
from functools import cache
from pathlib import Path
from typing import Annotated

import jinja2
import orjson
from fastapi import Depends
from starlette.requests import Request
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates, pass_context

__all__ = ["JinjaTemplates", "Template"]

import settings

static_folder = "static"


##
@pass_context  # context is required otherwise jinja2 caches the result in bytecode for constants
async def debug_asset_filter(_, path):
    txt = Path(os.path.join(static_folder, "assets-manifest.json")).read_text()
    return orjson.loads(txt).get(path)


@cache  # jinja caches that if input is a constant, but to be sure we cache it here too
async def asset_filter(path):
    return debug_asset_filter(None, path)


class JinjaTemplates:
    class JinjaException(Exception):
        def __init__(self, message):
            self.message = message

    templates = None

    def __init__(self, request: Request):
        self.request = request

    async def __call__(self, template_file, status_code=200, **kwargs):
        context = dict(request=self.request)
        context.update(kwargs)
        return HTMLResponse(await self.render_template(template_file, **context), status_code=status_code)

    @classmethod
    async def render_template(cls, template, **kwargs):
        if not cls.templates:
            raise cls.JinjaException("You must call initialize() before rendering templates.")
        template = cls.templates.get_template(template)
        return await template.render_async(**kwargs)

    @classmethod
    def initialize(
        cls,
        *,
        template_path: str,
        static_path=None,
        auto_reload=False,
        enable_async=True,
        **env_options,
    ) -> jinja2.Environment:
        global static_folder

        if not template_path:
            msg = "The template_folder must be specified."
            raise cls.JinjaException(msg)

        if not os.path.isdir(template_path):
            msg = f"The specified template folder must be a folder, it's not: {template_path}"
            raise cls.JinjaException(msg)

        cls.templates = Jinja2Templates(directory=template_path, enable_async=enable_async, **env_options)
        cls.templates.env.auto_reload = auto_reload

        static_folder = static_path

        if settings.DEBUG:
            cls.templates.env.filters["asset"] = debug_asset_filter
        else:
            cls.templates.env.filters["asset"] = asset_filter

        return cls.templates.env


Template = Annotated[JinjaTemplates, Depends(JinjaTemplates)]
