from typing import Annotated
from fastapi import Depends, APIRouter, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from api.domain.errors import InvalidUserNameOrPassword
from api.usecases.login import login as login_usecase

router = APIRouter(tags=["login"])

@router.post("/login")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    try:
        return login_usecase(form_data.username, form_data.password)
    except InvalidUserNameOrPassword:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
