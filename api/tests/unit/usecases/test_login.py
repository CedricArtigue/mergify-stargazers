from api.domain.entities import User
from api.domain.errors import InvalidUserNameOrPassword
from api.interface_adapters.gateways.user import InMemoryUserRepository
from api.usecases.login import login
import pytest # type: ignore

@pytest.fixture
def fake_user_repository():
    return InMemoryUserRepository()

@pytest.mark.unit
def test_login():
    user_repo = InMemoryUserRepository()
    user_repo.save(User(username='johndoe', hashed_password='fakehashedsecret', disabled=False))
    # test success path
    auth = login('johndoe', 'secret', user_repo)
    assert auth["access_token"] == 'johndoe'
    assert auth["token_type"] == 'bearer'

    # test error path
    try:
        auth = login('should', 'fail', user_repo)
        assert False
    except InvalidUserNameOrPassword:
        assert True        

