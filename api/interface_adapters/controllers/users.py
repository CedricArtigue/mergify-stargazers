from typing import Annotated
from fastapi import Depends, APIRouter

from api.interface_adapters.gateways.user import User, get_current_active_user

router = APIRouter(tags=["users"])

@router.get("/users/me")
async def get_me(current_user: Annotated[User, Depends(get_current_active_user)]):
    return current_user