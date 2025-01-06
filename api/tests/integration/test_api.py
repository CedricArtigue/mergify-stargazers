import os
import time
import alembic.config
import pytest # type: ignore
from sqlalchemy.exc import DataError, IntegrityError
from sqlalchemy.orm import sessionmaker
from starlette.testclient import TestClient

from api.main import app
from api.domain.entities import Todo, TodoFilter
from api.domain.repositories import ITodoRepository
from api.infrastructure.database.client import SQL_BASE, get_engine
from api.interface_adapters.gateways.todo import InMemoryTodoRepository, SQLTodoRepository

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
      yield c

@pytest.fixture(scope="module")
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
 
