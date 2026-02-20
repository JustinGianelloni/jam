from rich.table import Table

from cli.output import (
    create_table,
    is_piped,
    print_json,
    print_table,
    print_values,
)
from core.settings import get_settings
from models.user import User

SETTINGS = get_settings()


def _get_user_table(title: str) -> Table:
    return create_table(title, list(SETTINGS.console_user_fields.keys()))


def _add_user_rows(table: Table, users: list[User]) -> None:
    for user in users:
        row_values = [
            getattr(user, attr)
            for attr in SETTINGS.console_user_fields.values()
        ]
        table.add_row(*row_values)


def print_users(users: list[User], json: bool) -> None:
    if json:
        print_json(users)
    elif is_piped():
        print_values([user.id for user in users])
    else:
        table = _get_user_table(f"Users - Total Count: {len(users)}")
        _add_user_rows(table, users)
        print_table(table)
