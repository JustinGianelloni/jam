import asyncio

import typer

from api import systems as sys_api
from api import users as usr_api
from api.systems import (
    NoSystemsFoundError,
    SystemNotFoundError,
    SystemSearchEmptyError,
)
from api.users import UserNotFoundError
from cli.input import (
    resolve_optional_argument,
    resolve_optional_list_argument,
)
from cli.output import print_error, save_to_csv
from cli.system import presenter as sys_presenter
from cli.user import presenter as usr_presenter
from core.progress import progress_context
from core.settings import get_settings
from models.system import System

SETTINGS = get_settings()
app = typer.Typer()


@app.command(name="list")
def list_systems(
    filters: list[str] | None = typer.Option(
        None,
        "-f",
        "--filter",
        help="Any number of filters using JumpCloud's filter syntax, e.g. "
        "'osFamily:$eq:Windows'",
    ),
    csv_file: str | None = typer.Option(
        None,
        "--csv",
        help="Export result to specified CSV file",
    ),
    os: str | None = typer.Option(
        None,
        "-o",
        "--os",
        help="Filter systems by their operating system, e.g. 'Windows', "
        "'Max OS X', or 'Ubuntu'",
    ),
    os_family: str | None = typer.Option(
        None,
        "-f--family",
        help="Filter systems by their operating system family, e.g. "
        "'windows', 'darwin', or 'linux'",
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
    Returns a table of all systems in JumpCloud filtered by any provided flags.
    """
    if not filters:
        filters = []
    if os:
        filters.append(f"os:$eq:{os}")
    if os_family:
        filters.append(f"osFamily:$eq:{os_family}")
    try:
        with progress_context():
            systems = asyncio.run(sys_api.list_systems(filters))
    except NoSystemsFoundError as e:
        print_error(f"No systems found with the provided filters: {e.filters}")
    sys_presenter.print_systems(systems, json)
    if csv_file:
        save_to_csv(systems, csv_file, SETTINGS.csv_system_fields)


def _resolve_system_ids(
    system_ids: list[str] | None,
    hostname: str | None,
    serial: str | None,
    cmd: str,
) -> tuple[list[str], list[System] | None]:
    if all(v is None for v in (system_ids, hostname, serial)):
        print_error(f"No arguments specified. Use '{cmd} --help' for details.")
        raise typer.Exit(1)
    if sum(v is not None for v in (system_ids, hostname, serial)) > 1:
        print_error(
            f"Too many arguments specified. Use '{cmd} --help' for details."
        )
        raise typer.Exit(1)
    if system_ids:
        return system_ids, None
    for field, value in {
        "hostname": hostname,
        "serial": serial,
    }.items():
        if value:
            try:
                with progress_context():
                    systems = asyncio.run(sys_api.find_system(field, value))
            except SystemSearchEmptyError as e:
                print_error(f"No system found with {e.field} '{e.value}'")
                raise typer.Exit(1) from e
            return [system.id for system in systems], systems
    print_error("An unknown error has occurred.")
    raise typer.Exit(1)


@app.command(name="get")
def get_system(
    system_ids: list[str] | None = typer.Argument(
        None,
        help="One or more valid JumpCloud system IDs.",
    ),
    hostname: str | None = typer.Option(
        None,
        "-h",
        "--hostname",
        help="A system's hostname.",
    ),
    serial: str | None = typer.Option(
        None, "-s", "--serial", help="A system's serial number."
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
    Return a JumpCloud system by its ID, hostname, or serial number.
    """
    system_ids = resolve_optional_list_argument(system_ids)
    system_ids, systems = _resolve_system_ids(
        system_ids, hostname, serial, "jam system get"
    )
    if systems is None:
        try:
            with progress_context():
                systems = asyncio.run(sys_api.get_systems(system_ids))
        except SystemNotFoundError as e:
            print_error(f"No system found with system ID '{e.system_id}'")
            raise typer.Exit(1) from e
    sys_presenter.print_systems(systems, json)


@app.command(name="fde-key")
def fde_key(
    system_id: str | None = typer.Argument(
        None,
        help="A valid UUID for a JumpCloud system",
    ),
    hostname: str | None = typer.Option(
        None, "-h", "--hostname", help="A system's hostname."
    ),
    serial: str | None = typer.Option(
        None,
        "-s",
        "--serial",
        help="A system's serial number.",
    ),
) -> None:
    """
Returns the full disk encryption key for the specified system ID, \
hostname, or serial number.
    """
    system_id = resolve_optional_argument(system_id)
    system_ids, _ = _resolve_system_ids(
        [system_id] if system_id else None, hostname, serial, "jam system fde-key"
    )
    if len(system_ids) > 1:
        print_error(
            "More than one system found with provided search parameters."
        )
        raise typer.Exit(1)
    try:
        with progress_context():
            key = asyncio.run(sys_api.get_fde_key(system_ids[0]))
    except SystemNotFoundError as e:
        print_error(f"No system found with ID '{e.system_id}'")
        raise typer.Exit(1) from e
    sys_presenter.print_fde_key(key)


@app.command(name="bound-users")
def list_user_associations(
    system_id: str | None = typer.Argument(
        None,
        help="A valid UUID for a JumpCloud system",
    ),
    hostname: str | None = typer.Option(
        None,
        "-h",
        "--hostname",
        help="A system's hostname.",
    ),
    serial: str | None = typer.Option(
        None,
        "-s",
        "--serial",
        help="A system's serial number.",
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
    system_id = resolve_optional_argument(system_id)
    system_ids, _ = _resolve_system_ids(
        [system_id] if system_id else None, hostname, serial, "jam system bound-users"
    )
    if len(system_ids) > 1:
        print_error(
            "More than one system found with provided search parameters."
        )
        raise typer.Exit(1)
    with progress_context():
        try:
            associations = asyncio.run(
                sys_api.list_associations("user", system_ids[0])
            )
        except SystemNotFoundError as e:
            print_error(f"No system found with ID '{e.system_id}'")
            raise typer.Exit(1) from e
        user_ids = [
            association.to.id for association in associations if association.to
        ]
        try:
            users = asyncio.run(usr_api.get_users(user_ids))
        except UserNotFoundError as e:
            print_error(f"No user found with ID '{e.user_id}'")
            raise typer.Exit(1) from e
    usr_presenter.print_users(users, json)
