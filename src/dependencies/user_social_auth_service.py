from datetime import datetime
from typing import Annotated

from fastapi import Depends
from orjson import orjson
from pydantic import BaseModel, EmailStr
from rich.pretty import pprint
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.orm import joinedload

from db.dependencies import AsyncSession
from db.models import User, UserSocialAuth
from db.models.user import CachedUser


class UserInfo(BaseModel):
    sub: str
    name: str
    email: EmailStr
    locale: str


class UserService:
    class CouldNotCreateUser(Exception):
        pass

    class UserDisabled(Exception):
        pass

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_one(self, **kwargs) -> UserSocialAuth:
        stmt = select(UserSocialAuth).filter_by(**kwargs)
        return (await self._session.execute(stmt)).scalar_one()

    async def login_or_create_user(self, *, service: str, userinfo: UserInfo) -> CachedUser:
        stmt = select(UserSocialAuth).filter_by(service=service, sub=userinfo.sub).options(joinedload(UserSocialAuth.user))
        try:
            instance = (await self._session.execute(stmt)).scalar_one()
            if not instance.user.active:
                raise self.UserDisabled()
            return CachedUser.model_validate(instance)
        except NoResultFound:
            user = User(email=userinfo.email)
            instance = UserSocialAuth(service=service, user=user, **userinfo.model_dump())
            try:
                self._session.add(user)
                self._session.add(instance)
                await self._session.commit()
                return CachedUser.model_validate(instance)
            except IntegrityError as e:
                await self._session.rollback()
                try:
                    instance = (await self._session.execute(stmt)).scalar_one()
                    if not instance.user.active:
                        raise self.UserDisabled()
                    return CachedUser.model_validate(instance)
                except NoResultFound:
                    raise self.CouldNotCreateUser from e

    @classmethod
    async def load_user_from_session(cls, session_data: str) -> CachedUser | None:
        obj = orjson.loads(session_data)
        user = CachedUser.model_validate(obj)
        pprint(user)
        print(datetime.utcnow() - user.loaded_at)
        return user


UserServiceDependency = Annotated[UserService, Depends(UserService)]
