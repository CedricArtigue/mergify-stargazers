# This file holds domain entities interfaces encapsuling potential intra-model business logic (none in this simple example)
# NB: it could also hold a factory for each model, ensuring that business invariants are always met at instantiation time
# NB2: a single file for all models because of case simplicity, in a large scale project we should probably use a file per model
from pydantic import BaseModel

class User(BaseModel):
    username: str
    hashed_password: str
    disabled: bool = False

class Neighbour(BaseModel):
    repo: str
    stargazers: list[str]