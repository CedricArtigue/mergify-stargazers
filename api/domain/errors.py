class InvalidUserNameOrPassword(Exception):
    "Raised when login paramaters are incorrect"
    pass

class GithubRepositoryNotFound(Exception):
    "Raised when owner/repo tuples does not exist in github"
    pass

class GithubUserNotFound(Exception):
    "Raised when user does not exist in github"
    pass

class GithubRateLimitExceeded(Exception):
    "Raised when github rate limit is exceeded"
    pass

class UnknownError(Exception):
    "Raised when something unexpected happened"
    pass
