from rich.table import Table

from cli.output import (
    create_table,
    is_piped,
    print_json,
    print_table,
    print_values,
)
from core.settings import get_settings
from models.application import Application

SETTINGS = get_settings()


def _get_app_table(title: str) -> Table:
    return create_table(title, list(SETTINGS.console_app_fields.keys()))


def _add_app_rows(table: Table, apps: list[Application]) -> None:
    for app in apps:
        row_values = [
            str(getattr(app, attr))
            for attr in SETTINGS.console_app_fields.values()
        ]
        table.add_row(*row_values)


def print_applications(apps: list[Application], json: bool) -> None:
    if json:
        print_json(apps)
    elif is_piped():
        print_values([app.id for app in apps])
    else:
        table = _get_app_table(f"Applications - Total Count: {len(apps)}")
        _add_app_rows(table, apps)
        print_table(table)
