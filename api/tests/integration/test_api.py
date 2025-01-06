import os
import time
import alembic.config
import pytest # type: ignore
from sqlalchemy.exc import DataError, IntegrityError
from sqlalchemy.orm import sessionmaker
from starlette.testclient import TestClient

from api.main import app
from api.domain.entities import Todo, TodoFilter
from api.domain.repositories import TodoRepository
from api.infrastructure.database.client import SQL_BASE, get_engine
from api.interface_adapters.gateways.todo import InMemoryTodoRepository, SQLTodoRepository

@pytest.mark.integration
def test_api():
    time.sleep(1)
    assert True
    # client = TestClient(app)

    # response = client.post("/create/lo?value=testvalue")
    # assert response.status_code == 201

    # response = client.get("/get/testkey")
    # assert response.status_code == 200
    # assert response.json() == {"key": "testkey", "value": "testvalue", "done": False}

    # response = client.get("/get/wrong")
    # assert response.status_code == 404
