from api.domain.errors import InvalidUserNameOrPassword
from api.domain.repositories import IUserRepository
from api.interface_adapters.shared.auth import fake_hash_password

class AuthToken:
    access_token: str
    token_type: str

def login(username: str, password: str, user_repository: IUserRepository) -> AuthToken:
    user = user_repository.get_by_username(username)
    if not user:
        raise InvalidUserNameOrPassword
    hashed_password = fake_hash_password(password)
    if not hashed_password == user.hashed_password:
        raise InvalidUserNameOrPassword

    return {"access_token": user.username, "token_type": "bearer"}
