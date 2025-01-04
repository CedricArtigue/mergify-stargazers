from typing import Annotated
from fastapi import Depends
from fastapi import APIRouter

from api.repositories.user import User, get_current_active_user

router = APIRouter()

@router.get("/users/me")
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return current_user