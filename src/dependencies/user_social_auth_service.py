from typing import Annotated

from fastapi import Depends
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.orm import joinedload

from db.dependencies import AsyncSession
from db.models import User, UserSocialAuth


class UserInfo(BaseModel):
    sub: str
    name: str
    email: EmailStr
    locale: str


class UserSocialAuthService:
    class CouldNotCreateUser(Exception):
        pass

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_one(self, **kwargs) -> UserSocialAuth:
        stmt = select(UserSocialAuth).filter_by(**kwargs)
        return (await self._session.execute(stmt)).scalar_one()

    async def login_or_create_user(self, *, service: str, userinfo: UserInfo) -> UserSocialAuth:
        stmt = select(UserSocialAuth).filter_by(service=service, sub=userinfo.sub).options(joinedload(UserSocialAuth.user))
        try:
            return (await self._session.execute(stmt)).scalar_one()
        except NoResultFound:
            user = User(email=userinfo.email)
            instance = UserSocialAuth(service=service, user=user, **userinfo.model_dump())
            try:
                self._session.add(user)
                self._session.add(instance)
                await self._session.commit()
                return instance
            except IntegrityError as e:
                await self._session.rollback()
                try:
                    return (await self._session.execute(stmt)).scalar_one()
                except NoResultFound:
                    raise self.CouldNotCreateUser from e


UserSocialAuthDependency = Annotated[UserSocialAuthService, Depends(UserSocialAuthService)]
