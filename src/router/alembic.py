import io
import re

from alembic.config import Config
from fastapi import APIRouter

from alembic import command

router = APIRouter()


@router.get("/history")
def history():
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.attributes["configure_logger"] = False
    buffer = io.StringIO()
    alembic_cfg.stdout = buffer
    command.history(alembic_cfg, indicate_current=True)
    output = buffer.getvalue()
    buffer.close()
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
