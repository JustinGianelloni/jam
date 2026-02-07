from core.settings import Settings
from core.auth import TokenFactory
from rich.console import Console
from httpx import Client
from typing import Any
from rich.table import Table
from csv import DictWriter
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


def get_user_table(title: str) -> Table:
    table = Table(title=title)
    for field in SETTINGS.console_system_fields.keys():
        table.add_column(field)
    return table


def save_systems_to_csv(users: list[System], csv_file: str) -> None:
    keys = SETTINGS.csv_system_fields.values()
    with open(csv_file, "w") as file:
        writer = DictWriter(file, fieldnames=keys)
        writer.writeheader()
        writer.writerows(
            [user.model_dump(include=set(keys)) for user in users]
        )


def list_systems(filters: list[str] | None, csv_file: str | None) -> None:
    table = get_user_table("Systems")
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