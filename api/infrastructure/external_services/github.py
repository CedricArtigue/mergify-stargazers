import requests

from api.domain.errors import (
  GithubRepositoryNotFound, 
  GithubUserNotFound, 
  GithubRateLimitExceeded, 
  UnknownError
)
from api.domain.external_services import IGithubService

# GithubService implementing domain interface
class GithubService(IGithubService):
  def get_repo_stargazers(self, owner: str, repo: str):
    try:
      res = requests.get(f'https://api.github.com/repos/{owner}/{repo}/stargazers')
    except:
      raise UnknownError
    if (res.status_code == 200):
      return res.json()
    if (res.status_code == 404):
      raise GithubRepositoryNotFound
    if ((res.status_code == 403) or (res.status_code == 429)) and (res.headers['x-ratelimit-remaining'] == 0):
      raise GithubRateLimitExceeded

  # get list of starred repo for a given user
  def get_starred_repos(self, user: str):
    try:
      res = requests.get(f'https://api.github.com/users/{user}/starred')
    except:
      raise UnknownError
    if (res.status_code == 200):
      return res.json()
    if res.response.status_code == 404:
      raise GithubUserNotFound
    if ((res.status_code == 403) or (res.status_code == 429)) and (res.headers['x-ratelimit-remaining'] == 0):
      raise GithubRateLimitExceeded
