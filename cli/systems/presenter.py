from api import systems as api
from cli.output import (
    CONSOLE,
    create_table,
    print_json,
    print_table,
    print_value,
    save_to_csv,
    save_to_json,
)
from core.client import get_client
from core.settings import get_settings


def _get_settings():
    return get_settings()


def _get_system_table(title: str):
    return create_table(
        title, list(_get_settings().console_system_fields.keys())
    )


def _add_system_rows(table, systems: list) -> None:
    settings = _get_settings()
    for system in systems:
        row_values = [
            getattr(system, attr)
            for attr in settings.console_system_fields.values()
        ]
        table.add_row(*row_values)


def get_system(system_id: str, full: bool, json_file: str | None) -> None:
    """Get and display a single system."""
    system = api.get_system(get_client(), system_id)
    if json_file:
        save_to_json(system, json_file)
        return
    if full:
        print_json(system)
        return
    table = _get_system_table("System")
    _add_system_rows(table, [system])
    print_table(table)


def list_systems(filters: list[str] | None, csv_file: str | None) -> None:
    """List and display all systems matching filters."""
    systems = api.list_systems(get_client(), filters)
    table = _get_system_table("Systems")
    _add_system_rows(table, systems)
    print_table(table)
    if csv_file:
        save_to_csv(systems, csv_file, _get_settings().csv_system_fields)


def get_fde_key(system_id: str) -> None:
    """Get and display the FDE key for a system."""
    print_value(api.get_fde_key(get_client(), system_id))


def find_system(query: str) -> None:
    """Find systems by hostname or serial number."""
    systems = api.find_system(get_client(), query)
    if not systems:
        CONSOLE.print(f"No systems found matching '{query}'.")
        return
    if len(systems) == 1:
        print_value(systems[0].id)
        return
    table = _get_system_table("Search Results")
    _add_system_rows(table, systems)
    print_table(table)


def list_bound_systems(user_id: str) -> None:
    """List all systems bound to a user."""
    systems = api.list_bound_systems(get_client(), user_id)
    if not systems:
        CONSOLE.print(f"No devices found bound to user with ID '{user_id}'.")
        return
    if len(systems) == 1:
        print_value(systems[0])
        return
    table = create_table("Bound Systems", ["ID"])
    for system in systems:
        table.add_row(system)
    print_table(table)
