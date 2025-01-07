import os
from fastapi import Depends, HTTPException, status
from typing import Annotated

from api.domain.entities import User
from api.interface_adapters.gateways.user import UserInDB
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# TODO: remove fake user database
fake_users_db = {
    "johndoe": {
        "id": 0,
        "username": "johndoe",
        "hashed_password": "fakehashedsecret",
        "disabled": False,
    },
    "alice": {
        "id": 1,
        "username": "alice",
        "hashed_password": "fakehashedsecret2",
        "disabled": True,
    },
}

# TODO: use a real hash library
def fake_hash_password(password: str):
    return "fakehashed" + password

def fake_decode_token(token):
    # This doesn't provide any security at all
    # Check the next version
    user = get_user(fake_users_db, token)
    return user

def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    user = fake_decode_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
