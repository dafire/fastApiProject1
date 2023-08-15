from typing import Annotated

from fastapi import Depends
from starlette.requests import Request

from settings import Settings, get_settings
from utils.timing_middleware import record_timing

__all__ = ["RecordTiming"]

_settings = get_settings(Settings)


class _RecordTiming:
    def __init__(self, request: Request):
        self.request = request
        self.enabled = True

    def __call__(self, note: str | None = None):
        if _settings.debug and self.enabled:
            record_timing(self.request, note)


RecordTiming = Annotated[_RecordTiming, Depends(_RecordTiming)]
