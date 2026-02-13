import asyncio

import typer

from api import systems as sys_api
from api import users as usr_api
from cli.input import resolve_argument, resolve_list_argument
from cli.output import save_to_csv
from cli.systems import presenter as sys_presenter
from cli.users import presenter as usr_presenter
from core.settings import get_settings

app = typer.Typer()


@app.command(name="list")
def list_systems(
    filters: list[str] | None = typer.Option(
        None,
        "--filter",
        help="Any number of filters using JumpCloud's filter syntax, e.g. 'osFamily:$eq:Windows'",
    ),
    csv_file: str | None = typer.Option(
        None, "--csv", help="Export result to specified CSV file"
    ),
    os: str | None = typer.Option(
        None,
        "--os",
        help="Filter systems by their operating system, e.g. 'Windows', 'Max OS X', or 'Ubuntu'",
    ),
    os_family: str | None = typer.Option(
        None,
        "--os-family",
        help="Filter systems by their operating system family, e.g. 'windows', 'darwin', or 'linux'",
    ),
    json: bool = typer.Option(
        False,
        "-j",
        "--json",
        is_flag=True,
        help="Return a full JSON model of the system(s).",
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
    systems = asyncio.run(sys_api.list_systems(filters))
    sys_presenter.print_systems(systems, json)
    if csv_file:
        save_to_csv(systems, csv_file, get_settings().csv_system_fields)


@app.command(name="get")
def get_system(
    system_ids: list[str] | None = typer.Argument(
        None,
        help="A valid UUID for a JumpCloud system, e.g. '69879fa9b5be2f2184d700da'",
    ),
    json: bool = typer.Option(
        False,
        "-j",
        "--json",
        is_flag=True,
        help="Return a full JSON model of the system.",
    ),
) -> None:
    """
    Get a JumpCloud system by its UUID.
    """
    system_ids = resolve_list_argument(system_ids)
    systems = asyncio.run(sys_api.get_systems(system_ids))
    sys_presenter.print_systems(systems, json)


@app.command(name="fde-key")
def fde_key(
    system_id: str | None = typer.Argument(
        None,
        help="A valid UUID for a JumpCloud system, e.g. '69879fa9b5be2f2184d700da'",
    ),
) -> None:
    """
    Returns the full disk encryption key for the specified system UUID.
    """
    system_id = resolve_argument(system_id, "System ID")
    fde_key = asyncio.run(sys_api.get_fde_key(system_id))
    sys_presenter.print_fde_key(fde_key)


@app.command(name="find")
def find_system(
    query: str | None = typer.Argument(
        None, help="A valid hostname our serial number for a JumpCloud system"
    ),
    json: bool = typer.Option(
        False,
        "-j",
        "--json",
        is_flag=True,
        help="Return a full JSON model of the system(s).",
    ),
) -> None:
    """
    Find a JumpCloud system's UUID by its hostname or serial number. If the query returns multiple results, a table of matching systems will be displayed instead of a single UUID.
    """
    query = resolve_argument(query, "Hostname or serial number")
    systems = asyncio.run(sys_api.find_system(query))
    sys_presenter.print_systems(systems, json)


@app.command(name="bound-users")
def list_user_associations(
    system_id: str | None = typer.Argument(
        None,
        help="A valid UUID for a JumpCloud system, e.g. '69879fa9b5be2f2184d700da'",
    ),
    json: bool = typer.Option(
        False,
        "-j",
        "--json",
        is_flag=True,
        help="Return a full JSON model of the user(s).",
    ),
) -> None:
    """
    Find all users bound to a system.
    """
    system_id = resolve_argument(system_id, "System ID")
    associations = asyncio.run(sys_api.list_associations("user", system_id))
    user_ids = [
        association.to.id for association in associations if association.to
    ]
    users = asyncio.run(usr_api.get_users(user_ids))
    usr_presenter.print_users(users, json)
