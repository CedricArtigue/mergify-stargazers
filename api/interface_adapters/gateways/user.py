import os
from collections.abc import Iterator
from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.exc import DatabaseError
from sqlalchemy.orm import Session, sessionmaker

from api.domain.entities import User
from api.domain.repositories import IUserRepository
from api.infrastructure.database.client import SQL_BASE, get_engine

class UserInDB(SQL_BASE):
    __tablename__ = "app_user"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(length=128), nullable=False, unique=True)
    hashed_password = Column(String(length=128), nullable=False)
    disabled = Column(Boolean, default=False)

# In-memory implementation of interface
class InMemoryUserRepository(IUserRepository):
    def __init__(self):
        self.data = {}

    def save(self, user: User) -> None:
        self.data[user.username] = user

    def get_by_username(self, username: str) -> User | None:
        return self.data.get(username)

    # This provides no security, here token is set to be the username directly
    def get_by_token(self, token: str) -> User | None:
        return self.data.get(token)

# SQL Implementation of interface
class SQLUserRepository(IUserRepository):
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
            return User(username=instance.username, hashed_password=instance.hashed_password, disabled=instance.disabled)

        return None
    
    # This provides no security, here token is set to be the username directly
    def get_by_token(self, token: str) -> User | None:
        instance = self._session.query(UserInDB).filter(UserInDB.username == token).first()

        if instance:
            return User(username=instance.username, hashed_password=instance.hashed_password, disabled=instance.disabled)

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
