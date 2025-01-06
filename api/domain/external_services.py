class IGithubService:
    def get_repo_stargazers(self, owner: str, repo: str):
        raise NotImplementedError()

    def get_starred_repos(self, user: str):
        raise NotImplementedError()