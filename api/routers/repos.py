from fastapi import APIRouter, Depends, HTTPException
from api.repositories.repository import Neighbour
import pandas as pd
import requests

from api.repositories.user import get_current_active_user

router = APIRouter(
    prefix="/repos",
    tags=["repos"],
    dependencies=[Depends(get_current_active_user)],
    responses={404: {"description": "Not found"}},
)

@router.get("/{owner}/{name}/starneighbours", response_model=list[Neighbour] | None)
def get_neighbour_repositories(owner: str, name: str):
    # get target repo stargazers
    stargazers = requests.get(f'https://api.github.com/repos/{owner}/{name}/stargazers').json()
    df_stargazers = pd.DataFrame(stargazers).head(1) # TODO: remove limitation here

    # get list of starred repo for a given user, filtering out target repo
    def getStarred(user):
        starred = requests.get(f'https://api.github.com/users/{user}/starred')
        df_starred = pd.DataFrame(starred.json())['full_name']
        return df_starred[df_starred != f'{owner}/{name}'].to_list()

    # prepare dataset for grouping
    df = pd.DataFrame()
    df['login'] = df_stargazers['login']
    df['starred'] = df_stargazers['login'].map(getStarred)
    df = df.explode("starred")

    # Group users by neighbour repository
    df_tmp = df.groupby('starred').login.apply(list).reset_index()
    df_tmp['distance'] = df_tmp.login.map(len)
    df_tmp.sort_values('distance', ascending=False)

    neighbours = df_tmp\
        .sort_values('distance', ascending=False)\
        .rename(columns={"starred": "repo", "login": "stargazers"})\
        .to_dict('records')

    if not neighbours:
        raise HTTPException(status_code=404, detail="Repo not found")

    return neighbours