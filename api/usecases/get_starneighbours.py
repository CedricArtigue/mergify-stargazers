import pandas as pd
import requests

from api.domain.entities import Neighbour

# TODO: handle business domain errors, create a dedicated injected github service
# Core business logic of building starneighbour of a given repository
def get_starneighbours(owner: str, name: str) -> list[Neighbour]:
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

    return neighbours