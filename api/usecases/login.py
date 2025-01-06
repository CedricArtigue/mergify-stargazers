from api.domain.errors import InvalidUserNameOrPassword
from api.interface_adapters.gateways.user import UserInDB, fake_users_db

class AuthToken:
    access_token: str
    token_type: str

def fake_hash_password(password: str):
    return "fakehashed" + password

def login(username: str, password: str) -> AuthToken:
    user_dict = fake_users_db.get(username)
    if not user_dict:
        raise InvalidUserNameOrPassword    
    user = UserInDB(**user_dict)
    hashed_password = fake_hash_password(password)
    if not hashed_password == user.hashed_password:
        raise InvalidUserNameOrPassword

    return {"access_token": user.username, "token_type": "bearer"}
