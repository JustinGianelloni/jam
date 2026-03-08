import asyncio

import typer

from api import systems as sys_api
from api import users as usr_api
from api.systems import SystemNotFoundError
from api.users import (
    NoUsersFoundError,
    UserEmailNotFoundError,
    UserNotFoundError,
)
from cli.input import (
    resolve_argument,
    resolve_list_argument,
    resolve_optional_argument,
)
from cli.output import print_error, save_to_csv
from cli.system import presenter as sys_presenter
from cli.user import presenter as usr_presenter
from core.progress import progress_context
from core.settings import get_settings

SETTINGS = get_settings()
app = typer.Typer()


@app.command(name="list")
def list_users(
    filters: list[str] | None = typer.Option(
        None,
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
        "--department",
        help="Filter users by their department attribute, e.g. 'Engineering'",
    ),
    cost_center: str | None = typer.Option(
        None,
        "--cost-center",
        help="Filter users by their cost center attribute, e.g. "
        "'Data Engineering'",
    ),
    title: str | None = typer.Option(
        None,
        "--title",
        help="Filter users by their job title attribute, e.g. 'Data Engineer'",
    ),
    state: str | None = typer.Option(
        None,
        "--state",
        help="Filter users by their state in JumpCloud, e.g. "
        "'ACTIVATED', 'SUSPENDED', or 'STAGED'",
    ),
    employee_type: str | None = typer.Option(
        None,
        "--type",
        help="Filter users by their type in JumpCloud, e.g. "
        "'Full Time', 'Contractor', or 'Service'",
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
List all system users in JumpCloud.
Users can be filtered by specifying a flag with a value or by using \
JumpCloud's filter syntax.
For example, to filter for all activated users in the engineering department, \
you could use either '--state ACTIVATED --department Engineering' or \
'--filter state:$eq:ACTIVATED --filter department:$eq:Engineering'.
If both flag-based filters and filter syntax are used together, they will be \
combined into a single list of filters.
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


@app.command(name="get")
def get_user(
    user_ids: list[str] | None = typer.Argument(
        None,
        help="A valid UUID for a JumpCloud user, e.g. "
        "'685cb0f6ef36c7bd8ac56c24'",
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
Get a JumpCloud system user by their UUID. Use 'find-user' to get a user's \
UUID by their email address.
    """
    user_ids = resolve_list_argument(user_ids)
    try:
        with progress_context():
            users = asyncio.run(usr_api.get_users(user_ids))
    except UserNotFoundError as e:
        print_error(f"No user found with ID '{e.user_id}'")
        raise typer.Exit(1) from e
    usr_presenter.print_users(users, json)


@app.command(name="find")
def find_user(
    email: str | None = typer.Argument(
        None,
        help="A valid email address for a JumpCloud user.",
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
Find a JumpCloud user's UUID by their email address. If the query returns \
multiple results, a table of matching users will be displayed instead of a \
single UUID.
    """
    email = resolve_argument(email, "Email")
    try:
        users = asyncio.run(usr_api.find_user(email))
    except UserEmailNotFoundError as e:
        print_error(f"No user found with email '{e.email}'")
        raise typer.Exit(1) from e
    usr_presenter.print_users(users, json)


@app.command(name="bound-systems")
def bound_systems(
    user_id: str | None = typer.Argument(
        None,
        help="A valid UUID for a JumpCloud user, e.g. "
        "'685cb0f6ef36c7bd8ac56c24'",
    ),
    email: str | None = typer.Option(
        None,
        "-e",
        "--email",
        help="A valid email address for a JumpCloud user.",
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
    if user_id and email:
        msg = ("'--user_id' and '--email' are mutually exclusive. "
            "Use 'jam user bound-systems --help' for details.")
        raise typer.BadParameter(msg)
    if not user_id and not email:
        msg = ("'--user_id' or '--email' must be specified. "
            "Use 'jam user bound-systems --help' for details.")
        raise typer.BadParameter(msg, param_hint="'--user_id'")
    if email:
        try:
            user_ids = asyncio.run(usr_api.find_user(email))
            if len(user_ids) > 1:
                print_error(f"More than one user for for email '{email}'")
                raise typer.Exit(1)
            user_id = user_ids[0].id
        except UserEmailNotFoundError as e:
            print_error(f"No user found with email '{e.email}'")
            raise typer.Exit(1) from e
    if not user_id:
        msg = "'--user_id' or '--email' must be specified."
        raise typer.BadParameter(msg, param_hint="'--user_id'")
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
