import os
from typing import Annotated

import jinja2
from fastapi import Depends
from starlette.requests import Request
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates

__all__ = ["JinjaTemplates", "Template"]


class JinjaTemplates:
    class JinjaException(Exception):
        def __init__(self, message):
            self.message = message

    templates = None

    def __init__(self, request: Request):
        self.request = request

    def __call__(self, template_file, status_code=200, **kwargs):
        context = dict(request=self.request)
        context.update(kwargs)
        return HTMLResponse(self.render_template(template_file, **context), status_code=status_code)

    @classmethod
    def render_template(cls, template, **kwargs):
        if not cls.templates:
            raise cls.JinjaException("You must call initialize() before rendering templates.")
        return cls.templates.get_template(template).render(**kwargs)

    @classmethod
    def initialize(cls, template_path: str, auto_reload=False, **env_options) -> jinja2.Environment:
        if not template_path:
            msg = f"The template_folder must be specified."
            raise cls.JinjaException(msg)

        if not os.path.isdir(template_path):
            msg = f"The specified template folder must be a folder, it's not: {template_path}"
            raise cls.JinjaException(msg)

        cls.templates = Jinja2Templates(directory=template_path, **env_options)
        cls.templates.env.auto_reload = auto_reload
        return cls.templates.env


Template = Annotated[JinjaTemplates, Depends(JinjaTemplates)]