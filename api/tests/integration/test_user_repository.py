import os
import time
import alembic.config
import pytest # type: ignore
from sqlalchemy.orm import sessionmaker

from api.domain.entities import User
from api.domain.repositories import IUserRepository
from api.infrastructure.database.client import SQL_BASE, get_engine
from api.interface_adapters.gateways.user import InMemoryUserRepository, SQLUserRepository, UserInDB

@pytest.fixture
def fake_user_repository():
    return InMemoryUserRepository()

@pytest.fixture
def user_repository():
    time.sleep(1)
    alembicArgs = ["--raiseerr", "upgrade", "head"]
    alembic.config.main(argv=alembicArgs)

    engine = get_engine(os.getenv("DB_STRING"))
    session = sessionmaker(bind=engine)()

    yield SQLUserRepository(session)

    session.close()

    sessionmaker(bind=engine, autocommit=True)().execute(
        ";".join([f"TRUNCATE TABLE {t} CASCADE" for t in SQL_BASE.metadata.tables])
    )

@pytest.mark.integration
def test_contract_test(fake_user_repository: IUserRepository, user_repository: IUserRepository):
    for repository in [fake_user_repository, user_repository]:
        repository.save(UserInDB(username="johndoe", hashed_password="johndoesecret", disabled=False))

        new_user = repository.get_by_username("johndoe")
        assert new_user and new_user.username == "johndoe"
