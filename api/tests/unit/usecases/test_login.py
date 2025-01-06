from api.domain.errors import InvalidUserNameOrPassword
from api.usecases.login import login
import pytest # type: ignore

@pytest.mark.unit
def test_login():
    # test success path
    auth = login('johndoe', 'secret')
    assert auth["access_token"] == 'johndoe'
    assert auth["token_type"] == 'bearer'

    # test error path
    try:
        auth = login('should', 'fail')
        assert False
    except InvalidUserNameOrPassword:
        assert True        

