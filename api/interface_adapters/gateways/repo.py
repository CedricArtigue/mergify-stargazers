import os
from collections.abc import Iterator
from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.exc import DatabaseError
from sqlalchemy.orm import Session, sessionmaker

from api.domain.entities import Repo, RepoFilter
from api.domain.repositories import IRepoRepository
from api.infrastructure.database.client import SQL_BASE, get_engine

class RepoInDB(SQL_BASE):
    __tablename__ = "repo"

    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(length=128), nullable=False, unique=True)
    value = Column(String(length=128), nullable=False)
    done = Column(Boolean, default=False)

class InMemoryRepoRepository(IRepoRepository):  # In-memory implementation of interface
    def __init__(self):
        self.data = {}

    def save(self, repo: Repo) -> None:
        self.data[repo.key] = repo

    def get_by_key(self, key: str) -> Repo | None:
        return self.data.get(key)

    def get(self, repo_filter: RepoFilter) -> list[Repo]:
        all_matching_repos = filter(
            lambda repo: (not repo_filter.key_contains or repo_filter.key_contains in repo.key)
            and (not repo_filter.value_contains or repo_filter.value_contains in repo.value)
            and (not repo_filter.done or repo_filter.done == repo.done),
            self.data.values(),
        )

        return list(all_matching_repos)[: repo_filter.limit]


class SQLRepoRepository(IRepoRepository):  # SQL Implementation of interface
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

    def save(self, repo: Repo) -> None:
        self._session.add(RepoInDB(key=repo.key, value=repo.value))

    def get_by_key(self, key: str) -> Repo | None:
        instance = self._session.query(RepoInDB).filter(RepoInDB.key == key).first()

        if instance:
            return Repo(key=instance.key, value=instance.value, done=instance.done)

        return None

    def get(self, repo_filter: RepoFilter) -> list[Repo]:
        query = self._session.query(RepoInDB)

        if repo_filter.key_contains is not None:
            query = query.filter(RepoInDB.key.contains(repo_filter.key_contains))

        if repo_filter.value_contains is not None:
            query = query.filter(RepoInDB.value.contains(repo_filter.value_contains))

        if repo_filter.done is not None:
            query = query.filter(RepoInDB.done == repo_filter.done)

        if repo_filter.limit is not None:
            query = query.limit(repo_filter.limit)

        return [Repo(key=repo.key, value=repo.value, done=repo.done) for repo in query]

def create_repo_repository() -> Iterator[IRepoRepository]:
    session = sessionmaker(bind=get_engine(os.getenv("DB_STRING")))()
    repo_repository = SQLRepoRepository(session)

    try:
        yield repo_repository
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
