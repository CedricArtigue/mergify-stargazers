import os
import time
import alembic.config
import pytest # type: ignore
from sqlalchemy.exc import DataError, IntegrityError
from sqlalchemy.orm import sessionmaker

from api.main import app
from api.domain.entities import Repo, RepoFilter
from api.domain.repositories import IRepoRepository
from api.infrastructure.database.client import SQL_BASE, get_engine
from api.interface_adapters.gateways.repo import InMemoryRepoRepository, SQLRepoRepository

@pytest.fixture
def fake_repo_repository():
    return InMemoryRepoRepository()


@pytest.fixture
def repo_repository():
    time.sleep(1)
    alembicArgs = ["--raiseerr", "upgrade", "head"]
    alembic.config.main(argv=alembicArgs)

    engine = get_engine(os.getenv("DB_STRING"))
    session = sessionmaker(bind=engine)()

    yield SQLRepoRepository(session)

    session.close()

    sessionmaker(bind=engine, autocommit=True)().execute(
        ";".join([f"TRUNCATE TABLE {t} CASCADE" for t in SQL_BASE.metadata.tables])
    )

@pytest.mark.integration
def test_contract_test(fake_repo_repository: IRepoRepository, repo_repository: IRepoRepository):
    """See https://martinfowler.com/bliki/ContractTest.html"""

    repo = Repo(key="testkey", value="testvalue")

    for repository in [fake_repo_repository, repo_repository]:
        repository.save(repo)

        new_repo = repository.get_by_key("testkey")
        assert new_repo and new_repo.value == "testvalue"

        assert len(repository.get(RepoFilter(key_contains="e"))) == 1
        assert len(repository.get(RepoFilter(key_contains="e", limit=0))) == 0
        assert len(repository.get(RepoFilter(key_contains="v"))) == 0

        assert len(repository.get(RepoFilter(value_contains="v"))) == 1
        assert len(repository.get(RepoFilter(value_contains="e", limit=0))) == 0
        assert len(repository.get(RepoFilter(value_contains="k"))) == 0


@pytest.mark.integration
def test_repo_repository(repo_repository: SQLRepoRepository):
    with repo_repository as r:
        r.save(Repo(key="testkey", value="testvalue"))

    repo = r.get_by_key("testkey")
    assert repo.value == "testvalue"

    with pytest.raises(IntegrityError), repo_repository as r:
        r.save(Repo(key="testkey", value="not allowed: unique repo keys!"))

    with pytest.raises(DataError), repo_repository as r:
        r.save(Repo(key="too long", value=129 * "x"))


@pytest.mark.integration
def test_repo_repository_filter(repo_repository: SQLRepoRepository):
    with repo_repository as repo:
        repo.save(Repo(key="testkey", value="testvalue"))
        repo.save(Repo(key="abcde", value="v"))

    repos = repo.get(RepoFilter(key_contains="test"))
    assert len(repos) == 1
    assert repos[0].value == "testvalue"

    repos = repo.get(RepoFilter(key_contains="abcde"))
    assert len(repos) == 1
    assert repos[0].value == "v"

    assert len(repo.get(RepoFilter(key_contains="e"))) == 2
    assert len(repo.get(RepoFilter(key_contains="e", limit=1))) == 1
    assert len(repo.get(RepoFilter(value_contains="v"))) == 2
    assert len(repo.get(RepoFilter(done=True))) == 0
