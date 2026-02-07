from csv import DictWriter
from typing import Any, Optional

import typer
from httpx import Client
from rich.console import Console
from rich.table import Table

from adapters import SystemUsers
from core.auth import TokenFactory
from core.settings import Settings
from models.SystemUsers import SystemUser

TOKEN_FACTORY: TokenFactory = TokenFactory()
SETTINGS: Settings = Settings()

app = typer.Typer()
console = Console()


def get_client() -> Client:
    headers: dict[str, Any] = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": TOKEN_FACTORY.get_token(),
    }
    return Client(
        base_url=SETTINGS.JUMPCLOUD_API_URL,
        headers=headers,
        timeout=SETTINGS.TIMEOUT,
    )


def get_user_table(title: str) -> Table:
    table = Table(title=title)
    for field in SETTINGS.DEFAULT_CONSOLE_USER_FIELDS.keys():
        table.add_column(field)
    return table


def save_users_to_csv(users: list[SystemUser], csv_file: str) -> None:
    keys = SETTINGS.DEFAULT_CSV_USER_FIELDS
    with open(csv_file, "w") as file:
        writer = DictWriter(file, fieldnames=keys)
        writer.writeheader()
        writer.writerows([user.model_dump(include=set(keys)) for user in users])


@app.command()
def list_users(
    filters: list[str] = typer.Argument(
        None,
        help="Any number of filters using JumpCloud's filter syntax, e.g. 'employeeType:$eq:Contractor'",
    ),
    csv_file: Optional[str] = typer.Option(None, "--csv", help="Export result to specified CSV file")
) -> None:
    """
    List all system users in JumpCloud.
    """
    table = get_user_table("System Users")
    users = SystemUsers.list_all_system_users(get_client(), filters)
    for user in users:
        row_values = [getattr(user, attr) for attr in SETTINGS.DEFAULT_CONSOLE_USER_FIELDS.values()]
        table.add_row(*row_values)
    console.print(table)
    if csv_file:
        save_users_to_csv(users, csv_file)
        console.print(f"Exported {len(users)} users to '{csv_file}'.")


@app.command()
def get_user(
    user_id: str = typer.Argument(
        help="a UUID for a JumpCloud user, e.g. '685cb0f6ef36c7bd8ac56c24'"
    ),
) -> None:
    table = get_user_table("System User")
    user = SystemUsers.list_system_user(get_client(), user_id)
    row_values = [getattr(user, attr) for attr in SETTINGS.DEFAULT_CONSOLE_USER_FIELDS.values()]
    table.add_row(*row_values)
    console.print(table)


@app.command()
def find_user(email: str) -> None:
    console.print(SystemUsers.find_system_user(get_client(), email))


if __name__ == "__main__":
    app()
