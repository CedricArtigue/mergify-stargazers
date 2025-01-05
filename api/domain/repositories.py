# This file holds Domain Models Repository Interfaces 
from api.domain.models import Todo, TodoFilter

class TodoRepository:
    def __enter__(self):
        return self

    def __exit__(self, exc_type: type[Exception], exc_value: str, exc_traceback: str):
        pass

    def save(self, todo: Todo) -> None:
        raise NotImplementedError()

    def get_by_key(self, key: str) -> Todo | None:
        raise NotImplementedError()

    def get(self, todo_filter: TodoFilter) -> list[Todo]:
        raise NotImplementedError()
