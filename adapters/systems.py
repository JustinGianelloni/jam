from csv import DictWriter
from typing import Any

from httpx import Client
from rich.console import Console
from rich.table import Table

from core.auth import TokenFactory
from core.settings import Settings
from models.system import System
from services import systems as sys

SETTINGS = Settings()
TOKEN_FACTORY = TokenFactory()
CONSOLE = Console()


def get_client() -> Client:
    headers: dict[str, Any] = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": TOKEN_FACTORY.get_token(),
    }
    return Client(
        base_url=SETTINGS.api_url,
        headers=headers,
        timeout=SETTINGS.timeout,
    )


def get_system_table(title: str) -> Table:
    table = Table(title=title)
    for field in SETTINGS.console_system_fields.keys():
        table.add_column(field)
    return table


def get_system_list_table(title: str) -> Table:
    table = Table(title=title)
    table.add_column("ID")
    return table


def save_systems_to_csv(users: list[System], csv_file: str) -> None:
    fieldnames = SETTINGS.csv_system_fields.values()
    with open(csv_file, "w") as file:
        writer = DictWriter(file, fieldnames=fieldnames)
        writer.writerow({value: name for name, value in SETTINGS.csv_system_fields.items()})
        writer.writerows(
            [user.model_dump(include=set(fieldnames)) for user in users]
        )


def list_systems(filters: list[str] | None, csv_file: str | None) -> None:
    table = get_system_table("Systems")
    systems = sys.list_all_systems(get_client(), filters)
    for system in systems:
        row_values = [
            getattr(system, attr)
            for attr in SETTINGS.console_system_fields.values()
        ]
        table.add_row(*row_values)
    CONSOLE.print(table)
    if csv_file:
        save_systems_to_csv(systems, csv_file)
        CONSOLE.print(f"Exported {len(systems)} systems to '{csv_file}'.")


def get_system(system_id: str, full: bool) -> None:
    table = get_system_table("System User")
    system = sys.list_system(get_client(), system_id)
    if full:
        CONSOLE.print(system.model_dump(mode="json", exclude_none=True))
        return
    row_values = [
        getattr(system, attr)
        for attr in SETTINGS.console_system_fields.values()
    ]
    table.add_row(*row_values)
    CONSOLE.print(table)


def get_fde_key(system_id: str) -> None:
    CONSOLE.print(sys.get_fde_key(get_client(), system_id))


def find_system(query: str) -> None:
    systems = sys.find_system(get_client(), query)
    if not systems:
        CONSOLE.print(f"No systems found matching '{query}'.")
        return
    elif len(systems) == 1:
        CONSOLE.print(systems[0].id)
        return
    table = get_system_table("Search Results")
    for system in systems:
        row_values = [
            getattr(system, attr)
            for attr in SETTINGS.console_system_fields.values()
        ]
        table.add_row(*row_values)
    CONSOLE.print(table)


def list_bound_systems(user_id: str) -> None:
    systems = sys.list_bound_systems(get_client(), user_id)
    if not systems:
        CONSOLE.print(f"No devices found bound to user with ID '{user_id}'.")
        return
    if len(systems) == 1:
        CONSOLE.print(systems[0])
        return
    table = get_system_list_table("Bound Systems")
    for system in systems:
        table.add_row(system)
    CONSOLE.print(table)
