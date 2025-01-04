from pydantic import BaseModel

class Neighbour(BaseModel):
    repo: str
    stargazers: list[str]
