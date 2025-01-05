from functools import cache
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base

SQL_BASE = declarative_base()

@cache
def get_engine(db_string: str):
    return create_engine(db_string, pool_pre_ping=True)