from datetime import datetime
from typing import Annotated

from authlib.integrations.base_client import OAuthError
from authlib.integrations.starlette_client import OAuth
from fastapi import APIRouter, HTTPException, Path
from starlette import status
from starlette.requests import Request
from starlette.responses import RedirectResponse
from starlette.websockets import WebSocket

from db.models import User
from dependencies.user_social_auth_service import UserServiceDependency
from settings import AuthSettings, get_settings
from utils.jinja2_templates import Template
from utils.oauth.discord import Discord, Google, OAuthBase

_settings = get_settings(AuthSettings)

_backends: {str: OAuthBase} = {"google": Google, "discord": Discord}

router = APIRouter(prefix="/auth")


async def login_required(request: Request = None, websocket: WebSocket = None) -> User | None:
    if websocket:
        return None
    if request and request.user and request.user.active:
        return request.user
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)


@router.get("/")
async def login(template: Template):
    return await template("auth/login.html", backends=_backends)


@router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(request.url_for("login"), status_code=status.HTTP_303_SEE_OTHER)


@router.get("/login/{backend}")
async def authorize_url(request: Request, backend: Annotated[str, Path(...)]):
    if backend not in _backends:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    oauth = OAuth()
    oauth.register(name=backend, **_backends[backend].config)
    oauth_client = getattr(oauth, backend)
    redirect_uri = request.url_for("authorize", backend=backend)
    response = await oauth_client.authorize_redirect(request, redirect_uri)
    return response


@router.get("/{backend}")
async def authorize(request: Request, backend: Annotated[str, Path(...)], user_auth_service: UserServiceDependency):
    if backend not in _backends:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    try:
        oauth = OAuth()
        backend_obj: OAuthBase = _backends[backend]
        oauth.register(name=backend, **backend_obj.config)
        oauth_client = getattr(oauth, backend)
        token = await oauth_client.authorize_access_token(request)
        keys = list(filter(lambda key: key.startswith("_state_"), request.session.keys()))
        for key in keys:
            request.session.pop(key)
        if "userinfo" in token:
            raw_userinfo = token["userinfo"]
        else:
            raw_userinfo = await oauth_client.userinfo(token=token)
        userinfo = backend_obj.normalize_userinfo(raw_userinfo)

        social_user = await user_auth_service.login_or_create_user(service=backend_obj.service, userinfo=userinfo)
        redirect_url = request.session.get("login_redirect", "/")
        request.session.clear()
        request.session["user"] = social_user.user.to_dict()
        request.session["user_updated"] = datetime.utcnow()
        return RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)
    except OAuthError as e:
        request.session["error"] = str(e.error)
        return RedirectResponse(request.url_for("login"), status_code=status.HTTP_303_SEE_OTHER)
    except user_auth_service.CouldNotCreateUser:
        request.session["error"] = "Could not login user with this service"
        return RedirectResponse(request.url_for("login"), status_code=status.HTTP_303_SEE_OTHER)
