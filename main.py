import sys
from typing import Optional

import typer

from adapters import system_users, systems
from core.auth import TokenFactory
from core.settings import Settings

TOKEN_FACTORY: TokenFactory = TokenFactory()
SETTINGS: Settings = Settings()

app = typer.Typer()


@app.command()
def list_users(
    filters: Optional[list[str]] = typer.Option(
        None,
        "--filter",
        help="Any number of filters using JumpCloud's filter syntax, e.g. 'employeeType:$eq:Contractor'",
    ),
    csv_file: Optional[str] = typer.Option(
        None, "--csv", help="Export result to specified CSV file"
    ),
    department: Optional[str] = typer.Option(
        None,
        "--department",
        help="Filter users by their department attribute, e.g. 'Engineering'",
    ),
    cost_center: Optional[str] = typer.Option(
        None,
        "--cost-center",
        help="Filter users by their cost center attribute, e.g. 'Data Engineering'",
    ),
    title: Optional[str] = typer.Option(
        None,
        "--title",
        help="Filter users by their job title attribute, e.g. 'Data Engineer'",
    ),
    state: Optional[str] = typer.Option(
        None,
        "--state",
        help="Filter users by their state in JumpCloud, e.g. 'ACTIVATED', 'SUSPENDED', or 'STAGED'",
    ),
) -> None:
    """
    List all system users in JumpCloud.
    Users can be filtered by specifying a flag with a value or by using JumpCloud's filter syntax.
    For example, to filter for all activated users in the engineering department,
    you could use either '--state ACTIVATED --department Engineering' or '--filter state:$eq:ACTIVATED --filter department:$eq:Engineering'.
    If both flag-based filters and filter syntax are used together, they will be combined into a single list of filters.
    """
    if not filters:
        filters = []
    if department:
        filters.append(f"department:$eq:{department}")
    if cost_center:
        filters.append(f"costCenter:$eq:{cost_center}")
    if title:
        filters.append(f"jobTitle:$eq:{title}")
    if state:
        filters.append(f"state:$eq:{state}")
    system_users.list_users(filters, csv_file)


@app.command()
def get_user(
    user_id: Optional[str] = typer.Argument(
        None,
        help="A valid UUID for a JumpCloud user, e.g. '685cb0f6ef36c7bd8ac56c24'",
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
def find_user(
    email: Optional[str] = typer.Argument(
        None, help="A valid email address for a JumpCloud user."
    ),
) -> None:
    """
    Find a JumpCloud user's UUID by their email address. If the query returns multiple results, a table of matching users will be displayed instead of a single UUID.
    """
    if email is None:
        if not sys.stdin.isatty():
            email = sys.stdin.read().strip()
        else:
            typer.echo("Error: Missing argument 'EMAIL'.")
    system_users.find_user(email)


@app.command()
def list_systems(
    filters: Optional[list[str]] = typer.Option(
        None,
        "--filter",
        help="Any number of filters using JumpCloud's filter syntax, e.g. 'osFamily:$eq:Windows'",
    ),
    csv_file: Optional[str] = typer.Option(
        None, "--csv", help="Export result to specified CSV file"
    ),
    os: Optional[str] = typer.Option(
        None,
        "--os",
        help="Filter systems by their operating system, e.g. 'Windows', 'Max OS X', or 'Ubuntu'",
    ),
    os_family: Optional[str] = typer.Option(
        None,
        "--os-family",
        help="Filter systems by their operating system family, e.g. 'windows', 'darwin', or 'linux'",
    ),
) -> None:
    """
    List all systems in JumpCloud.
    Systems can be filtered by specifying a flag with a value or by using JumpCloud's filter syntax.
    For example, to filter for all Windows systems, you could use either '--os Windows' or '--filter os:$eq:Windows'.
    If both flag-based filters and filter syntax are used together, they will be combined into a single list of filters.
    """
    if not filters:
        filters = []
    if os:
        filters.append(f"os:$eq:{os}")
    if os_family:
        filters.append(f"osFamily:$eq:{os_family}")
    systems.list_systems(filters, csv_file)


@app.command()
def get_system(
    system_id: Optional[str] = typer.Argument(
        None,
        help="A valid UUID for a JumpCloud system, e.g. '69879fa9b5be2f2184d700da'",
    ),
    full: bool = typer.Option(
        False,
        "--full",
        is_flag=True,
        help="Display all available fields",
    ),
) -> None:
    """
    Get a JumpCloud system by its UUID.
    """
    if system_id is None:
        if not sys.stdin.isatty():
            system_id = sys.stdin.read().strip()
        else:
            typer.echo("Error: Missing argument 'SYSTEM_ID'.")
    systems.get_system(system_id, full)


@app.command()
def fde_key(
    system_id: Optional[str] = typer.Argument(
        None,
        help="A valid UUID for a JumpCloud system, e.g. '69879fa9b5be2f2184d700da'",
    ),
) -> None:
    """
    Returns the full disk encryption key for the specified system UUID.
    """
    if system_id is None:
        if not sys.stdin.isatty():
            system_id = sys.stdin.read().strip()
        else:
            typer.echo("Error: Missing argument 'SYSTEM_ID'.")
    systems.get_fde_key(system_id)


@app.command()
def find_system(
    query: Optional[str] = typer.Argument(
        None, help="A valid hostname our serial number for a JumpCloud system"
    ),
) -> None:
    """
    Find a JumpCloud system's UUID by its hostname or serial number. If the query returns multiple results, a table of matching systems will be displayed instead of a single UUID.
    """
    if query is None:
        if not sys.stdin.isatty():
            query = sys.stdin.read().strip()
        else:
            typer.echo("Error: Missing argument 'EMAIL'.")
    systems.find_system(query)


@app.command()
def bound_systems(
    query: Optional[str] = typer.Argument(
        None,
        help="A valid UUID for a JumpCloud user, e.g. '685cb0f6ef36c7bd8ac56c24'",
    ),
) -> None:
    """
    Find all systems bound to a JumpCloud user by the user's UUID. If the query returns multiple results, a table of matching systems will be displayed instead of a list of UUIDs.
    """
    if query is None:
        if not sys.stdin.isatty():
            query = sys.stdin.read().strip()
        else:
            typer.echo("Error: Missing argument 'USER_ID'.")
    systems.list_bound_systems(query)


if __name__ == "__main__":
    app()
