import asyncio

import typer

from api import groups as grp_api
from api import users as usr_api
from cli.groups import presenter
from cli.input import resolve_argument
from cli.output import save_to_csv
from core.progress import progress_context
from core.settings import get_settings
from models.user import User

SETTINGS = get_settings()
app = typer.Typer()


@app.command(name="list")
def list_user_groups(
    filters: list[str] | None = typer.Option(
        None,
        "--filter",
        help="Any number of filters using JumpCloud's v2 filter syntax, e.g. "
        "'name:search:Engineering'",
    ),
    csv_file: str | None = typer.Option(
        None,
        "--csv",
        help="Export result to specified CSV file",
    ),
    name: str | None = typer.Option(
        None,
        "--name",
        help="Filter user groups by their name, e.g. 'Engineering'",
    ),
    json: bool = typer.Option(
        False,
        "-j",
        "--json",
        is_flag=True,
        help="Return a full JSON model of the user group(s).",
    ),
) -> None:
    """
List all user groups in JumpCloud.
User groups can be filtered by specifying a flag with a value or by using \
JumpCloud's v2 filter syntax.
If both flag-based filters and filter syntax are used together, they will be \
combined into a single list of filters.
    """
    if not filters:
        filters = []
    if name:
        filters.append(f"name:eq:{name}")
    groups = asyncio.run(grp_api.list_groups(filters))
    presenter.print_groups(groups, json)
    if csv_file:
        save_to_csv(groups, csv_file, SETTINGS.csv_group_fields)


@app.command(name="get-members")
def get_group_members(
    group_id: str | None = typer.Argument(
        None,
        help="A valid UUID for a JumpCloud group, e.g. "
        "'689e1335e907ee000186085f'",
    ),
    csv_file: str | None = typer.Option(
        None,
        "--csv",
        help="Export result to specified CSV file",
    ),
    json: bool = typer.Option(
        False,
        "-j",
        "--json",
        is_flag=True,
        help="Return a full JSON model of the group's members.",
    ),
) -> None:
    """
    List all members of a JumpCloud user group.
    """
    group_id = resolve_argument(group_id, "Group ID")

    async def fetch_data() -> tuple[list[User], list[str]]:
        _users, _members = await asyncio.gather(
            usr_api.list_users([]),
            grp_api.get_group_members(group_id),
        )
        return _users, _members

    with progress_context():
        users, members = asyncio.run(fetch_data())
    user_dict = {user.id: user for user in users}
    member_list = [user_dict[member] for member in members]
    presenter.print_group_members(member_list, json)
    if csv_file:
        save_to_csv(member_list, csv_file, SETTINGS.csv_user_fields)
