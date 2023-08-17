import os
from pathlib import Path
from typing import Annotated

import jinja2
import orjson
from fastapi import Depends
from loguru import logger
from starlette.requests import Request
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates, pass_context

from settings import Settings, get_settings

__all__ = ["JinjaTemplates", "Template"]

_settings = get_settings(Settings)


def get_manifest(folder: str = "frontend") -> dict[str, str]:
    """
    Retrieves the manifest file for the specified folder.

    :param folder: The folder in which the manifest file is located. Defaults to "frontend".
    :return: A dictionary containing the contents of the manifest file.
    """
    manifest_file_path = Path(_settings.static_folder) / folder / "assets-manifest.json"

    try:
        manifest_data = manifest_file_path.read_text(encoding="utf-8")
        return orjson.loads(manifest_data)  # pylint: disable=maybe-no-member
    except orjson.JSONDecodeError as exc:  # pylint: disable=maybe-no-member
        logger.error("Could not parse frontend manifest {}", exc)
        return {}


@pass_context  # context is required otherwise jinja2 caches the result in bytecode for constants
def debug_asset_filter(_, path):
    path = "frontend" + "/" + get_manifest("frontend").get(path)
    logger.debug("asset: {}", path)
    return path


def asset_filter(path):
    path = "frontend" + "/" + get_manifest("frontend").get(path)
    logger.debug("asset: {}", path)
    return path


class JinjaTemplates:
    class JinjaException(Exception):
        def __init__(self, message):
            self.message = message

    templates = None

    def __init__(self, request: Request):
        self.request = request

    async def __call__(self, template_file, status_code=200, **kwargs):
        context = {"request": self.request}
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
        enable_async=True,
        **env_options,
    ) -> jinja2.Environment:
        if not _settings.template_folder:
            msg = "The template_folder must be specified."
            raise cls.JinjaException(msg)

        if not os.path.isdir(_settings.template_folder):
            msg = f"The specified template folder must be a folder, it's not: {_settings.template_folder}"
            raise cls.JinjaException(msg)

        cls.templates = Jinja2Templates(directory=_settings.template_folder, enable_async=enable_async, **env_options)
        cls.templates.env.auto_reload = _settings.debug
        cls.templates.env.globals["settings"] = _settings.model_dump(exclude={"secret_key"})

        if _settings.debug:
            cls.templates.env.filters["asset"] = debug_asset_filter
        else:
            cls.templates.env.filters["asset"] = asset_filter

        return cls.templates.env


Template = Annotated[JinjaTemplates, Depends(JinjaTemplates)]
