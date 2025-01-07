import os
from fastapi import Depends, HTTPException, status
from typing import Annotated

from api.domain.entities import User
from api.domain.repositories import IUserRepository
from api.interface_adapters.gateways.user import UserInDB, create_user_repository
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# TODO: use a real hash library
def fake_hash_password(password: str):
    return "fakehashed" + password

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    user_repository: IUserRepository = Depends(create_user_repository)
):
    # This provide no security, we should retrieve user via a real token, not the username
    user = user_repository.get_by_token(token)
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
