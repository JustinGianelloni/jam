from api import users as api
from cli.output import (
    CONSOLE,
    create_table,
    is_piped,
    print_json,
    print_table,
    print_values,
    save_to_csv,
)
from core.settings import get_settings
from models.user import User


def _get_user_table(title: str):
    return create_table(title, list(get_settings().console_user_fields.keys()))


def _add_user_rows(table, users: list[User]) -> None:
    settings = get_settings()
    for user in users:
        row_values = [
            getattr(user, attr)
            for attr in settings.console_user_fields.values()
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
