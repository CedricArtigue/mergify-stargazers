import requests

# get list of stargazers for a given owner/repo tuple
def get_repo_stargazers(owner: str, repo: str):
    return requests.get(f'https://api.github.com/repos/{owner}/{repo}/stargazers').json()

# get list of starred repo for a given user
def get_starred_repos(user: str):
    return requests.get(f'https://api.github.com/users/{user}/starred').json()
