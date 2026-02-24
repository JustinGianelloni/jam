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

def print_group_members(members: list[User], json: bool) -> None:
    if json:
        print_json(members)
    elif is_piped():
        print_values([member.id for member in members])
    else:
        table = _get_user_table(f"Group Members - Total Count: {len(members)}")
        _add_user_rows(table, members)
        print_table(table)
