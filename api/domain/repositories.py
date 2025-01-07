# This file holds Domain Models Repository Interfaces 
from api.domain.entities import Repo, RepoFilter, User

class IRepoRepository:
    def __enter__(self):
        return self

    def __exit__(self, exc_type: type[Exception], exc_value: str, exc_traceback: str):
        pass

    def save(self, repo: Repo) -> None:
        raise NotImplementedError()

    def get_by_key(self, key: str) -> Repo | None:
        raise NotImplementedError()

    def get(self, filter: RepoFilter) -> list[Repo]:
        raise NotImplementedError()

class IUserRepository:
    def __enter__(self):
        return self

    def __exit__(self, exc_type: type[Exception], exc_value: str, exc_traceback: str):
        pass

    def save(self, user: User) -> None:
        raise NotImplementedError()

    def get_by_username(self, username: str) -> User | None:
        raise NotImplementedError()
    
    def get_by_token(self, token: str) -> User | None:
        raise NotImplementedError()