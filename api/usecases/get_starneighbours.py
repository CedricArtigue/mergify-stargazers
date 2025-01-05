import pandas as pd

from api.domain.entities import Neighbour
from api.infrastructure.external_services.github import get_repo_stargazers, get_starred_repos

# TODO: remove MAX_USERS limitation in future version
MAX_USERS = 1

# Core business logic of building starneighbour of a given repository
def get_starneighbours(owner: str, name: str) -> list[Neighbour]:
    # get list of stargazers for a given repo
    df_stargazers = pd.DataFrame(get_repo_stargazers(owner, name)).head(MAX_USERS)

    # get list of starred repo for a given user, filtering out target repo
    def getStarred(user):
        df_starred = pd.DataFrame(get_starred_repos(user))['full_name']
        return df_starred[df_starred != f'{owner}/{name}'].to_list()

    # prepare dataset for grouping
    df_prepared = pd.DataFrame()
    df_prepared['stargazers'] = df_stargazers.login
    df_prepared['repo'] = df_stargazers.login.map(getStarred)
    df_prepared = df_prepared.explode("repo")

    # Group users by starred repo
    df_grouped = df_prepared.groupby('repo').stargazers.apply(list).reset_index()

    return df_grouped.to_dict('records')