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
def list_users(
    filters: list[str] | None = typer.Option(
        None,
        "--filter",
        help="Any number of filters using JumpCloud's filter syntax, e.g. 'employeeType:$eq:Contractor'",
    ),
    csv_file: str | None = typer.Option(
        None, "--csv", help="Export result to specified CSV file"
    ),
    department: str | None = typer.Option(
        None,
        "--department",
        help="Filter users by their department attribute, e.g. 'Engineering'",
    ),
    cost_center: str | None = typer.Option(
        None,
        "--cost-center",
        help="Filter users by their cost center attribute, e.g. 'Data Engineering'",
    ),
    title: str | None = typer.Option(
        None,
        "--title",
        help="Filter users by their job title attribute, e.g. 'Data Engineer'",
    ),
    state: str | None = typer.Option(
        None,
        "--state",
        help="Filter users by their state in JumpCloud, e.g. 'ACTIVATED', 'SUSPENDED', or 'STAGED'",
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
    users = asyncio.run(usr_api.list_users(filters))
    usr_presenter.print_users(users, json)
    if csv_file:
        save_to_csv(users, csv_file, get_settings().csv_user_fields)


@app.command(name="get")
def get_user(
    user_ids: list[str] | None = typer.Argument(
        None,
        help="A valid UUID for a JumpCloud user, e.g. '685cb0f6ef36c7bd8ac56c24'",
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
    Get a JumpCloud system user by their UUID. Use 'find-user' to get a user's UUID by their email address.
    """
    user_ids = resolve_list_argument(user_ids)
    users = asyncio.run(usr_api.get_users(user_ids))
    usr_presenter.print_users(users, json)


@app.command(name="find")
def find_user(
    email: str | None = typer.Argument(
        None, help="A valid email address for a JumpCloud user."
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
    Find a JumpCloud user's UUID by their email address. If the query returns multiple results, a table of matching users will be displayed instead of a single UUID.
    """
    email = resolve_argument(email, "Email")
    users = asyncio.run(usr_api.find_user(email))
    usr_presenter.print_users(users, json)


@app.command(name="bound-systems")
def bound_systems(
    user_id: str | None = typer.Argument(
        None,
        help="A valid UUID for a JumpCloud user, e.g. '685cb0f6ef36c7bd8ac56c24'",
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
    Find all systems bound to a JumpCloud user by the user's UUID. If the query returns multiple results, a table of matching systems will be displayed instead of a list of UUIDs.
    """
    user_id = resolve_argument(user_id, "User ID")
    system_ids = asyncio.run(usr_api.list_bound_systems(user_id))
    systems = asyncio.run(sys_api.get_systems(system_ids))
    sys_presenter.print_systems(systems, json)
