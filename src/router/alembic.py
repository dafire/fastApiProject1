import io
import re
from typing import Annotated

from alembic import command
from alembic.config import Config
from fastapi import APIRouter
from rich.pretty import pprint


class AlembicUpgrade(BaseModel):
    revision: str


@database_router.post("/upgrade")
def alembic_upgrade(body: Annotated[AlembicUpgrade, Body(...)]):
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.attributes["configure_logger"] = False
    buffer = io.StringIO()
    alembic_cfg.stdout = buffer
    command.upgrade(alembic_cfg, revision=body.revision)
    output = buffer.getvalue()
    buffer.close()
    return {"output": output}


class Alembic(object):
    def __init__(self, config="alembic.ini"):
        self.cfg = Config(config)
        self.cfg.attributes["configure_logger"] = False
        self.buffer = io.StringIO()
        self.cfg.stdout = self.buffer

    def __enter__(self):
        return self

    def get_buffer(self):
        return self.buffer.getvalue()

    def __exit__(self, type, value, traceback):
        self.buffer.close()


@router.post("/upgrade")
def upgrade():
    with Alembic() as alembic:
        command.upgrade(alembic.cfg, "head")
        output = alembic.get_buffer()
        pprint(output)
    return {"message": "Upgrade successful"}


@router.get("/history")
def history():
    with Alembic() as alembic:
        command.history(alembic.cfg, indicate_current=True)
        output = alembic.get_buffer()
    regex = r"(?P<parent>\S+) -> (?P<target>\w+)\W{0,1}(?P<tags>.*), (?P<message>.+)"
    matches = re.finditer(regex, output, re.MULTILINE)
    rows = []
    upgrade_possible = True
    for match in matches:
        data = match.groupdict()
        tags = data["tags"].split(" ")
        data["deletion_possible"] = False
        data["upgrade_possible"] = False
        data["current"] = False
        data["downgrade_possible"] = False
        if "(current)" in tags:
            data["current"] = True
        elif upgrade_possible:
            data["upgrade_possible"] = True
            if "(head)" in tags:
                data["deletion_possible"] = True
        else:
            data["downgrade_possible"] = True
        del data["tags"]
        rows.append(data)
    return rows
