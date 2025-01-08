from typing import Annotated
from fastapi import Depends, APIRouter

from api.domain.entities import User
from api.interface_adapters.shared.auth import get_current_active_user

router = APIRouter(tags=["users"])

@router.get("/users/me")
async def get_me(current_user: Annotated[User, Depends(get_current_active_user)]):
    return current_user