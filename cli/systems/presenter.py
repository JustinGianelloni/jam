from cli.output import (
    create_table,
    is_piped,
    print_json,
    print_table,
    print_values,
)
from core.settings import get_settings
from models.system import System


def _get_system_table(title: str):
    return create_table(
        title, list(get_settings().console_system_fields.keys())
    )


def _add_system_rows(table, systems: list[System]) -> None:
    settings = get_settings()
    for system in systems:
        row_values = [
            getattr(system, attr)
            for attr in settings.console_system_fields.values()
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
