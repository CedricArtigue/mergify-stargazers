import pytest # type: ignore

from api.domain.errors import GithubRepositoryNotFound, GithubUserNotFound
from api.domain.entities import Neighbour
from api.domain.external_services import IGithubService
from api.usecases.get_starneighbours import get_starneighbours

# unit testing of get_starneighbours usecase
# following DIP SOLID principle, we bypass Github dependency by injecting a mocked service
class GithubServiceMocked(IGithubService):
  def get_repo_stargazers(self, owner: str, repo: str):
    if owner == 'MergifyIO' and repo == "mergify-cli":
      return [{ "login": 'cedric'}, { "login": 'julien' }, { "login": 'mehdi' }]
    raise GithubRepositoryNotFound

  # get list of starred repo for a given user
  def get_starred_repos(self, user: str):
    if user == 'cedric':
        return [{ "full_name": 'hello/world'}, { "full_name": 'MergifyIO/mergify-cli'}, { "full_name": 'cedric/mergify-stargazers'}] 
    if user == 'mehdi':
        return [{ "full_name": 'hello/world'}, { "full_name": 'MergifyIO/mergify-cli'}]
    if user == 'julien':
        return [{ "full_name": 'MergifyIO/mergify-cli'}]
    raise GithubUserNotFound


@pytest.mark.unit
def test_get_starneighbours():
    # test success path
    target_starneighbours = [
        {'repo': 'hello/world', 'stargazers': ['mehdi', 'cedric']},
        {'repo': 'cedric/mergify-stargazers', 'stargazers': ['cedric']}
    ]
    def deep_sort(sn: list[Neighbour]):
        return sorted([{ "repo": x["repo"], "stargazers": sorted(x["stargazers"])} for x in sn], key=lambda x: x['repo'])

    starneighbours = get_starneighbours('MergifyIO', 'mergify-cli', 3, GithubServiceMocked())
    assert deep_sort(starneighbours) == deep_sort(target_starneighbours)

    # test error path
    try:
        starneighbours = get_starneighbours('must', 'fail', 3, GithubServiceMocked())
        assert False
    except GithubRepositoryNotFound:
       assert True
