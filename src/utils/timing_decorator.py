from typing import Annotated

from fastapi import Depends
from starlette.requests import Request

import settings
from utils.timing_middleware import record_timing

__all__ = ["RecordTiming"]


class _RecordTiming:
    def __init__(self, request: Request):
        self.request = request
        self.enabled = True

    def __call__(self, note: str | None = None):
        if self.enabled:
            record_timing(self.request, note)


RecordTiming = Annotated[_RecordTiming, Depends(_RecordTiming)]
