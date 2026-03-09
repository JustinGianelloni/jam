import asyncio

import typer

from api import systems as sys_api
from api import users as usr_api
from api.systems import SystemNotFoundError
from api.users import (
    NoUsersFoundError,
    UserNotFoundError,
    UserSearchEmptyError,
)
from cli.input import (
    resolve_optional_argument,
    resolve_optional_list_argument,
)
from cli.output import print_error, save_to_csv
from cli.system import presenter as sys_presenter
from cli.user import presenter as usr_presenter
from core.progress import progress_context
from core.settings import get_settings
from models.user import State

SETTINGS = get_settings()
app = typer.Typer()


@app.command(name="list")
def list_users(
    filters: list[str] | None = typer.Option(
        None,
        "-f",
        "--filter",
        help="Any number of filters using JumpCloud's filter syntax, e.g. "
        "'employeeType:$eq:Contractor'",
    ),
    csv_file: str | None = typer.Option(
        None,
        "--csv",
        help="Export result to specified CSV file",
    ),
    department: str | None = typer.Option(
        None,
        "-d",
        "--department",
        help="Filter users by their department attribute.",
    ),
    cost_center: str | None = typer.Option(
        None,
        "-c",
        "--cost-center",
        help="Filter users by their cost center attribute.",
    ),
    title: str | None = typer.Option(
        None,
        "-t",
        "--title",
        help="Filter users by their job title attribute.",
    ),
    state: State | None = typer.Option(
        None,
        "-s",
        "--state",
        help="Filter users by their state in JumpCloud.",
    ),
    employee_type: str | None = typer.Option(
        None,
        "-t",
        "--type",
        help="Filter users by their type in JumpCloud.",
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
    Returns a table of all users in JumpCloud filtered by any provided flags.
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
    if employee_type:
        filters.append(f"employeeType:$eq:{employee_type}")
    try:
        with progress_context():
            users = asyncio.run(usr_api.list_users(filters))
    except NoUsersFoundError as e:
        print_error(f"No users found with provided filters: {e.filters}")
        raise typer.Exit(1) from e
    usr_presenter.print_users(users, json)
    if csv_file:
        save_to_csv(users, csv_file, SETTINGS.csv_user_fields)


def _resolve_user_ids(
    user_ids: list[str] | None,
    email: str | None,
    username: str | None,
    displayname: str | None,
    cmd: str,
) -> list[str]:
    if all(v is None for v in (user_ids, email, username, displayname)):
        print_error(f"No arguments specified. Use '{cmd} --help' for details.")
        raise typer.Exit(1)
    if (
        sum(v is not None for v in (user_ids, email, username, displayname))
        > 1
    ):
        print_error(
            f"Too many arguments specified. Use '{cmd} --help' for details."
        )
        raise typer.Exit(1)
    if user_ids:
        return user_ids
    for field, value in {
        "email": email,
        "username": username,
        "displayname": displayname,
    }.items():
        if value:
            try:
                with progress_context():
                    users = asyncio.run(usr_api.find_user(field, value))
            except UserSearchEmptyError as e:
                print_error(f"No user found with {e.field} '{e.value}'")
                raise typer.Exit(1) from e
            return [user.id for user in users]
    print_error("An unknown error has occurred.")
    raise typer.Exit(1)


@app.command(name="get")
def get_user(
    user_ids: list[str] | None = typer.Argument(
        None,
        help="One or more valid JumpCloud user IDs.",
    ),
    email: str | None = typer.Option(
        None,
        "-e",
        "--email",
        help="A valid email address for a JumpCloud user.",
    ),
    username: str | None = typer.Option(
        None,
        "-u",
        "--username",
        help="A valid username for a JumpCloud user.",
    ),
    displayname: str | None = typer.Option(
        None,
        "-d",
        "--displayname",
        help="A valid displayname for a JumpCloud user.",
    ),
    json: bool = typer.Option(
        False,
        "-j",
        "--json",
        is_flag=True,
        help="Return a full JSON model of the user.",
    ),
) -> None:
    """
    Return a JumpCloud user by their UUID, email, or username.
    """
    user_ids = resolve_optional_list_argument(user_ids)
    user_ids = _resolve_user_ids(user_ids, email, username, displayname, "get")
    try:
        with progress_context():
            users = asyncio.run(usr_api.get_users(user_ids))
    except UserNotFoundError as e:
        print_error(f"No user found with ID '{e.user_id}'")
        raise typer.Exit(1) from e
    usr_presenter.print_users(users, json)


@app.command(name="bound-systems")
def bound_systems(
    user_id: str | None = typer.Argument(
        None,
        help="A valid JumpCloud user ID.",
    ),
    email: str | None = typer.Option(
        None,
        "-e",
        "--email",
        help="A valid email address for a JumpCloud user.",
    ),
    username: str | None = typer.Option(
        None,
        "-u",
        "--username",
        help="A valid username for a JumpCloud user.",
    ),
    displayname: str | None = typer.Option(
        None,
        "-d",
        "--displayname",
        help="A valid displayname for a JumpCloud user.",
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
    Returns a table of all systems bound to a JumpCloud user.
    """
    user_id = resolve_optional_argument(user_id)
    user_ids = _resolve_user_ids(
        [user_id] if user_id else None,
        email,
        username,
        displayname,
        "bound_systems",
    )
    if len(user_ids) > 1:
        print_error(
            "More than one user found with provided search parameters."
        )
        raise typer.Exit(1)
    user_id = user_ids[0]
    try:
        system_ids = asyncio.run(usr_api.list_bound_systems(user_id))
    except UserNotFoundError as e:
        print_error(f"No user found with ID '{e.user_id}'")
        raise typer.Exit(1) from e
    if not system_ids:
        print_error(f"No systems bound to user with ID '{user_id}'")
        raise typer.Exit(1)
    try:
        systems = asyncio.run(sys_api.get_systems(system_ids))
    except SystemNotFoundError as e:
        print_error(f"No system found with ID '{e.system_id}'")
        raise typer.Exit(1) from e
    sys_presenter.print_systems(systems, json)
