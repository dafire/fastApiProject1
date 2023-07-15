from fastapi import APIRouter

from utils.session_route import SessionRoute

router = APIRouter(route_class=SessionRoute, prefix="/auth")


@router.get("/login")
async def login():
    return "login"
