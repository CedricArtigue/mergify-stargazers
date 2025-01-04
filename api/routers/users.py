from typing import Annotated
from fastapi import Depends
from fastapi import APIRouter

from api.repositories.user import User, get_current_active_user

router = APIRouter(tags=["users"])

@router.get("/users/me")
async def get_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return current_user