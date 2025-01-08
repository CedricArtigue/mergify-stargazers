import os
import time
import alembic.config
from fastapi.testclient import TestClient
import pytest # type: ignore
from api.main import app
from sqlalchemy.orm import sessionmaker

from api.domain.repositories import IUserRepository
from api.infrastructure.database.client import SQL_BASE, get_engine
from api.interface_adapters.gateways.user import InMemoryUserRepository, SQLUserRepository, UserInDB

@pytest.fixture
def fake_user_repository():
    return InMemoryUserRepository()

@pytest.fixture
def user_repository():
    time.sleep(1)
    alembic.config.main(argv=["--raiseerr", "upgrade", "head"])
    engine = get_engine(os.getenv("DB_STRING"))
    session = sessionmaker(bind=engine)()
    yield SQLUserRepository(session)
    session.close()
    # sessionmaker(bind=engine, autocommit=True)().execute(
    #     ";".join([f"TRUNCATE TABLE {t} CASCADE" for t in SQL_BASE.metadata.tables])
    # )

@pytest.mark.integration
def test_contract_test(fake_user_repository: IUserRepository, user_repository: IUserRepository):
    for repository in [fake_user_repository, user_repository]:
        repository.save(UserInDB(username="janedoe", hashed_password="secret2", disabled=False))

        new_user = repository.get_by_username("janedoe")
        assert new_user and new_user.username == "janedoe"

# testing the api
@pytest.fixture()
def client():
    with TestClient(app) as c:
      yield c

@pytest.fixture()
def test_user():
    return {"username": "johndoe", "password": "secret"}

def test_login(client, test_user):
  response = client.post("/login", data=test_user)
  assert response.status_code == 200
  token = response.json()["access_token"]
  assert token is not None
  return token

@pytest.mark.integration
def test_api(client, test_user):
    time.sleep(1)
    # test 404, page does not exist
    response = client.get("/fail")
    assert response.status_code == 404

    # test_login and retrieve token for subsequent authenticated routes tests
    token = test_login(client, test_user)

    # verify that user is loggedin
    response = client.get("/users/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    me = response.json()
    assert me['username'] == 'johndoe'

    # verify that user is loggedin
    response = client.get("/repos/MergifyIO/mergify-cli/starneighbours", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    neighbours = response.json()
    assert neighbours is not None
 
