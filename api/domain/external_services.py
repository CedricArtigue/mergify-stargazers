class IGithubService:
    def get_repo_stargazers(owner: str, repo: str):
        raise NotImplementedError()

    def get_starred_repos(user: str):
        raise NotImplementedError()