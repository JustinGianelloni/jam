from csv import DictWriter
from typing import Any

from httpx import Client
from rich.console import Console
from rich.table import Table

from core.auth import TokenFactory
from core.settings import Settings
from models.system_user import SystemUser
from services import system_users

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
    for field in SETTINGS.console_user_fields.keys():
        table.add_column(field)
    return table


def save_users_to_csv(users: list[SystemUser], csv_file: str) -> None:
    keys = SETTINGS.csv_user_fields.values()
    with open(csv_file, "w") as file:
        writer = DictWriter(file, fieldnames=keys)
        writer.writeheader()
        writer.writerows(
            [user.model_dump(include=set(keys)) for user in users]
        )


def get_user(user_id: str, full: bool) -> None:
    table = get_user_table("System User")
    user = system_users.list_system_user(get_client(), user_id)
    if full:
        CONSOLE.print(user.model_dump(mode="json", exclude_none=True))
        return
    row_values = [
        getattr(user, attr) for attr in SETTINGS.console_user_fields.values()
    ]
    table.add_row(*row_values)
    CONSOLE.print(table)


def list_users(filters: list[str], csv_file: str | None) -> None:
    table = get_user_table("System Users")
    users = system_users.list_all_system_users(get_client(), filters)
    for user in users:
        row_values = [
            getattr(user, attr)
            for attr in SETTINGS.console_user_fields.values()
        ]
        table.add_row(*row_values)
    CONSOLE.print(table)
    if csv_file:
        save_users_to_csv(users, csv_file)
        CONSOLE.print(f"Exported {len(users)} users to '{csv_file}'.")


def find_user(email: str) -> None:
    CONSOLE.print(system_users.find_system_user(get_client(), email))
