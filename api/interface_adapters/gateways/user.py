import os
from fastapi import Depends, HTTPException, status
from collections.abc import Iterator
from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.exc import DatabaseError
from sqlalchemy.orm import Session, sessionmaker
from typing import Annotated

from api.domain.entities import User
from api.domain.repositories import IUserRepository
from api.infrastructure.database.client import SQL_BASE, get_engine
from api.interface_adapters.shared.auth import oauth2_scheme

class UserInDB(SQL_BASE):
    __tablename__ = "app_user"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(length=128), nullable=False, unique=True)
    hashed_password = Column(String(length=128), nullable=False)
    disabled = Column(Boolean, default=False)

# TODO: seed database with those users and use
fake_users_db = {
    "johndoe": {
        "id": 0,
        "username": "johndoe",
        "hashed_password": "fakehashedsecret",
        "disabled": False,
    },
    "alice": {
        "id": 1,
        "username": "alice",
        "hashed_password": "fakehashedsecret2",
        "disabled": True,
    },
}

def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


def fake_decode_token(token):
    # This doesn't provide any security at all
    # Check the next version
    user = get_user(fake_users_db, token)
    return user

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    user = fake_decode_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


# Implementation of IUserRepository interface
class InMemoryUserRepository(IUserRepository):  # In-memory implementation of interface
    def __init__(self):
        self.data = {}

    def save(self, user: User) -> None:
        self.data[user.username] = user

    def get_by_username(self, username: str) -> User | None:
        return self.data.get(username)


class SQLUserRepository(IUserRepository):  # SQL Implementation of interface
    def __init__(self, session):
        self._session: Session = session

    def __exit__(self, exc_type: type[Exception], exc_value: str, exc_traceback: str) -> None:
        if any([exc_type, exc_value, exc_traceback]):
            self._session.rollback()
            return

        try:
            self._session.commit()
        except DatabaseError as e:
            self._session.rollback()
            raise e

    def save(self, user: User) -> None:
        self._session.add(UserInDB(username=user.username, hashed_password=user.hashed_password, disabled=user.disabled))

    def get_by_username(self, username: str) -> User | None:
        instance = self._session.query(UserInDB).filter(UserInDB.username == username).first()

        if instance:
            return User(username=instance.username, disabled=instance.disabled)

        return None

def create_user_repository() -> Iterator[IUserRepository]:
    session = sessionmaker(bind=get_engine(os.getenv("DB_STRING")))()
    repository = SQLUserRepository(session)

    try:
        yield repository
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
