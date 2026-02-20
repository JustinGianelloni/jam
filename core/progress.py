from collections.abc import Generator
from contextlib import contextmanager
from contextvars import ContextVar

from rich.progress import Progress, TaskID

_progress_ctx: ContextVar[Progress | None] = ContextVar(
    "progress", default=None
)


@contextmanager
def progress_context() -> Generator[Progress]:
    progress = Progress()
    token = _progress_ctx.set(progress)
    try:
        with progress:
            yield progress
    finally:
        _progress_ctx.reset(token)


def get_progress() -> Progress | None:
    return _progress_ctx.get()


def add_task(
    description: str, total: int, completed: int = 0
) -> TaskID | None:
    progress = get_progress()
    if progress:
        return progress.add_task(description, total=total, completed=completed)
    return None


def update_task(task_id: TaskID | None, advance: int) -> None:
    if task_id is None:
        return
    progress = get_progress()
    if progress:
        progress.update(task_id, advance=advance)
