import sys
from typing import Optional

import typer
from rich.console import Console

from adapters import system_users, systems
from core.auth import TokenFactory
from core.settings import Settings

TOKEN_FACTORY: TokenFactory = TokenFactory()
SETTINGS: Settings = Settings()

app = typer.Typer()
console = Console()


@app.command()
def list_users(
    filters: list[str] = typer.Argument(
        None,
        help="Any number of filters using JumpCloud's filter syntax, e.g. 'employeeType:$eq:Contractor'",
    ),
    csv_file: Optional[str] = typer.Option(
        None, "--csv", help="Export result to specified CSV file"
    ),
) -> None:
    """
    List all system users in JumpCloud.
    """
    system_users.list_users(filters, csv_file)


@app.command()
def get_user(
    user_id: Optional[str] = typer.Argument(
        None,
        help="a UUID for a JumpCloud user, e.g. '685cb0f6ef36c7bd8ac56c24'",
    ),
    full: bool = typer.Option(
        False, "--full", is_flag=True, help="Display all available fields"
    ),
) -> None:
    """
    Get a JumpCloud system user by their UUID. Use 'find-user' to get a user's UUID by their email address.
    """
    if user_id is None:
        if not sys.stdin.isatty():
            user_id = sys.stdin.read().strip()
        else:
            typer.echo("Error: Missing argument 'USER_ID'.")
    system_users.get_user(user_id, full)


@app.command()
def find_user(email: Optional[str] = typer.Argument(None, help="A valid email address for a JumpCloud user.")) -> None:
    """
    Find a JumpCloud user's UUID by their email address. The email can be a partial search, but multiple results will return a ValueError.
    """
    if email is None:
        if not sys.stdin.isatty():
            email = sys.stdin.read().strip()
        else:
            typer.echo("Error: Missing argument 'EMAIL'.")
    system_users.find_user(email)


@app.command()
def list_systems(
        filters: list[str] = typer.Argument(
            None,
            help="Any number of filters using JumpCloud's filter syntax, e.g. 'osFamily:$eq:Windows'",
        ),
        csv_file: Optional[str] = typer.Option(
            None, "--csv", help="Export result to specified CSV file"
        ),
) -> None:
    """
    List all systems in JumpCloud.
    """
    systems.list_systems(filters, csv_file)


if __name__ == "__main__":
    app()
