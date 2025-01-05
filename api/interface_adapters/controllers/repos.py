from fastapi import APIRouter, Depends, HTTPException

from api.domain.entities import Neighbour
from api.interface_adapters.gateways.user import get_current_active_user
from api.usecases.get_starneighbours import get_starneighbours as get_starneighbours_usecase
from api.domain.errors import GithubRepositoryNotFound

router = APIRouter(
    prefix="/repos",
    tags=["repos"],
    dependencies=[Depends(get_current_active_user)],
    responses={404: {"description": "Not found"}},
)

@router.get("/{owner}/{name}/starneighbours", response_model=list[Neighbour] | None)
def get_starneighbours(owner: str, name: str):
    try:
        neighbours = get_starneighbours_usecase(owner, name)
    except GithubRepositoryNotFound:
        raise HTTPException(status_code=404, detail="This repository does not exist on github")
    except Exception:
        raise HTTPException(status_code=500, detail="Internal Error, we'll investigate")
    return neighbours