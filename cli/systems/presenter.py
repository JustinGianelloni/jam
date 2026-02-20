from rich.table import Table

from cli.output import (
    create_table,
    is_piped,
    print_json,
    print_table,
    print_values,
)
from core.settings import get_settings
from models.system import System

SETTINGS = get_settings()


def _get_system_table(title: str) -> Table:
    return create_table(
        title,
        list(SETTINGS.console_system_fields.keys()),
    )


def _add_system_rows(table: Table, systems: list[System]) -> None:
    for system in systems:
        row_values = [
            getattr(system, attr)
            for attr in SETTINGS.console_system_fields.values()
        ]
        table.add_row(*row_values)


def print_systems(systems: list[System], json: bool) -> None:
    if json:
        print_json(systems)
    elif is_piped():
        print_values([system.id for system in systems])
    else:
        table = _get_system_table(f"Systems - Total Count: {len(systems)}")
        _add_system_rows(table, systems)
        print_table(table)


def print_fde_key(fde_key: str) -> None:
    print_values([fde_key])
