from collections.abc import Generator
from contextlib import contextmanager
from contextvars import ContextVar

from rich.console import Console
from rich.progress import Progress, TaskID

_progress_ctx: ContextVar[Progress | None] = ContextVar(
    "progress", default=None
)
_console_ctx: ContextVar[Console | None] = ContextVar(
    "console", default=None
)


@contextmanager
def progress_context() -> Generator[Progress]:
    console = Console()
    progress = Progress(console=console)
    token_p = _progress_ctx.set(progress)
    token_c = _console_ctx.set(console)
    try:
        with progress:
            yield progress
    finally:
        _progress_ctx.reset(token_p)
        _console_ctx.reset(token_c)


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


def get_console() -> Console:
    return _console_ctx.get() or Console()
