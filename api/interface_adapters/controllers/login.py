from typing import Annotated
from fastapi import Depends, APIRouter, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from api.domain.errors import InvalidUserNameOrPassword
from api.domain.repositories import IUserRepository
from api.interface_adapters.gateways.user import create_user_repository
from api.usecases.login import login as login_usecase

router = APIRouter(tags=["login"])

@router.post("/login")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], 
    user_repository: IUserRepository = Depends(create_user_repository)
):
    try:
        return login_usecase(form_data.username, form_data.password, user_repository)
    except InvalidUserNameOrPassword:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
