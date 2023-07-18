from abc import ABC, abstractmethod

from dependencies.user_social_auth_service import UserInfo
from settings import AuthSettings, get_settings

_settings = get_settings(AuthSettings)


class OAuthBase(ABC):
    @property
    @abstractmethod
    def config(self) -> dict:
        pass

    @property
    @abstractmethod
    def service(self) -> str:
        pass

    @classmethod
    @abstractmethod
    def normalize_userinfo(cls, userinfo: dict) -> UserInfo:
        pass


class Discord(OAuthBase):
    service = "discord"
    config = dict(
        client_id=_settings.discord_client_id,
        client_secret=_settings.discord_client_secret,
        access_token_url="https://discordapp.com/api/oauth2/token",
        api_base_url="https://discord.com/api/",
        authorize_url="https://discord.com/api/oauth2/authorize",
        userinfo_endpoint="https://discord.com/api/users/%40me",
        client_kwargs={"token_endpoint_auth_method": "client_secret_post", "scope": "identify email"},
    )

    @classmethod
    def normalize_userinfo(cls, userinfo: dict) -> UserInfo:
        return UserInfo(sub=userinfo["id"], name=userinfo["global_name"], email=userinfo["email"], locale=userinfo["locale"])


class Google(OAuthBase):
    service = "google"
    config = dict(
        client_id=_settings.google_client_id,
        client_secret=_settings.google_client_secret,

        access_token_url="https://oauth2.googleapis.com/token",
        # api_base_url="",
        authorize_url="https://accounts.google.com/o/oauth2/v2/auth",
        userinfo_endpoint="https://openidconnect.googleapis.com/v1/userinfo",
        jwks_uri="https://www.googleapis.com/oauth2/v3/certs",
        # server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={"scope": "openid email profile"},
    )

    @classmethod
    def normalize_userinfo(cls, userinfo: dict) -> UserInfo:
        return UserInfo(sub=userinfo["sub"], name=userinfo["name"], email=userinfo["email"], locale=userinfo["locale"])
