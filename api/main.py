from fastapi import Depends, FastAPI, HTTPException
from starlette.responses import RedirectResponse
from starlette.status import HTTP_201_CREATED

import pandas as pd
import requests

from api.repository import Neighbour

app = FastAPI(swagger_ui_parameters={"tryItOutEnabled": True})

@app.get("/")
async def root():
    return RedirectResponse(app.docs_url)

# ================================================================================================ #
# Route for testing
# ================================================================================================ #
@app.get("/repos/{owner}/{name}/starneighbours", response_model=list[Neighbour] | None)
def repos(owner: str, name: str):
    # get stargazers from github API
    stargazers = requests.get(f'https://api.github.com/repos/{owner}/{name}/stargazers').json()
    df_stargazers = pd.DataFrame(stargazers).head(10) # TODO: remove limitation here

    # get list of starred repo for a given user
    def getStarred(user):
        starred = requests.get(f'https://api.github.com/users/{user}/starred')
        df_starred = pd.DataFrame(starred.json())['full_name']
        return df_starred[df_starred != f'{owner}/{name}'].to_list()

    # Process
    df = pd.DataFrame()
    df['login'] = df_stargazers['login']
    df['starred'] = df_stargazers['login'].map(getStarred)
    df = df.explode("starred")

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