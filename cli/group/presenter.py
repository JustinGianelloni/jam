from rich.table import Table

from cli.output import (
    create_table,
    is_piped,
    print_json,
    print_table,
    print_values,
)
from core.settings import get_settings
from models.group import Group

SETTINGS = get_settings()


def _get_group_table(title: str) -> Table:
    return create_table(title, list(SETTINGS.console_group_fields.keys()))


def _add_group_rows(table: Table, groups: list[Group]) -> None:
    for group in groups:
        row_values = [
            getattr(group, attr)
            for attr in SETTINGS.console_group_fields.values()
        ]
        table.add_row(*row_values)


def print_groups(groups: list[Group], json: bool) -> None:
    if json:
        print_json(groups)
    elif is_piped():
        print_values([group.id for group in groups])
    else:
        table = _get_group_table(f"User Groups - Total Count: {len(groups)}")
        _add_group_rows(table, groups)
        print_table(table)
