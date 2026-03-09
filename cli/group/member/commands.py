import asyncio
from pathlib import Path

import typer

from api import groups as grp_api
from api import users as usr_api
from cli.group.member import presenter as member_presenter
from cli.group.member.exceptions import MemberChangeError
from cli.input import (
    read_csv_list,
    resolve_list_argument,
    resolve_optional_argument,
)
from cli.output import print_error, print_result, save_to_csv
from core.progress import add_task, progress_context, update_task
from core.settings import get_settings
from models.group import Group
from models.user import User

SETTINGS = get_settings()
app = typer.Typer()


@app.command(name="list")
def get_group_members(
    group_ids: list[str] | None = typer.Argument(
        None,
        help="A valid ID for a JumpCloud group",
    ),
    name: str | None = typer.Option(
        None,
        "-n",
        "--name",
        help="An exact or partial match for a JumpCloud group name."
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
    group_ids = resolve_list_argument(group_ids)

    async def fetch_data() -> tuple[list[User], list[str]]:
        _users, _members = await asyncio.gather(
            usr_api.list_users([]),
            grp_api.get_groups_members(group_ids),
        )
        return _users, _members

    with progress_context():
        users, members = asyncio.run(fetch_data())
    user_dict = {user.id: user for user in users}
    member_list = list(
        {member: user_dict[member] for member in members}.values()
    )
    member_presenter.print_group_members(member_list, json)
    if csv_file:
        save_to_csv(member_list, csv_file, SETTINGS.csv_user_fields)


def get_group_by_name(group_name: str) -> list[Group]:
    groups = asyncio.run(grp_api.list_groups([f"name:eq:{group_name}"]))
    if not groups:
        print_error(f"No group found with name: {group_name}")
        raise typer.Exit(1)
    if len(groups) > 1:
        print_error(f"{len(groups)} groups found with name: {group_name}")
        raise typer.Exit(1)
    return groups


def get_groups_by_csv(path: Path, group_dict: dict[str, Group]) -> list[Group]:
    groups = read_csv_list(path)
    if not groups:
        print_error(f"No groups found in path: {path}")
        raise typer.Exit(1)
    return [group_dict[group] for group in groups]


def get_user_by_email(email: str) -> list[User]:
    users = asyncio.run(usr_api.list_users([f"email:$eq:{email}"]))
    if not users:
        print_error(f"No user found with email: {email}")
        raise typer.Exit(1)
    if len(users) > 1:
        print_error(f"{len(users)} users found with email: {email}")
        raise typer.Exit(1)
    return users


def get_users_by_csv(path: Path, user_dict: dict[str, User]) -> list[User]:
    users = read_csv_list(path)
    if not users:
        print_error(f"No users found in path: {path}")
        raise typer.Exit(1)
    return [user_dict[user] for user in users]


def resolve_groups(
    group_id: str | None,
    group_name: str | None,
    group_csv: Path | None,
    group_dict: dict[str, Group],
) -> list[Group]:
    if group_id:
        groups = [asyncio.run(grp_api.get_group(group_id))]
    elif group_name:
        groups = get_group_by_name(group_name)
    elif group_csv:
        groups = get_groups_by_csv(group_csv, group_dict)
    else:
        print_error(
            "No group(s) specified. Pass a group as an argument, "
            "by using the '--name' option or via --group_csv"
        )
        raise typer.Exit(1)
    return groups


def resolve_users(
    user_id: str | None,
    email: str | None,
    user_csv: Path | None,
    user_dict: dict[str, User],
) -> list[User]:
    if user_id:
        users = [asyncio.run(usr_api.get_user(user_id))]
    elif email:
        users = get_user_by_email(email)
    elif user_csv:
        users = get_users_by_csv(user_csv, user_dict)
    else:
        print_error(
            "No user(s) specified. Specify a user using --user, --email, or "
            "--user_csv"
        )
        raise typer.Exit(1)
    return users


@app.command(name="add")
def add_group_member(
    group_id: str | None = typer.Option(
        None,
        help="A valid UUID for a JumpCloud group, e.g. "
        "'689e1335e907ee000186085f'",
    ),
    user_id: str | None = typer.Option(
        None,
        "-u",
        "--user",
        help="A valid UUI for a JumpCloud user, e.g. "
        "'685cb0f6ef36c7bd8ac56c24'",
    ),
    email: str | None = typer.Option(
        None,
        "-e",
        "--email",
        help="A valid email address for a JumpCloud user.",
    ),
    group_name: str | None = typer.Option(
        None,
        "-n",
        "--name",
        help="A valid name for a JumpCloud group.",
    ),
    user_csv: Path | None = typer.Option(
        None,
        "--user-csv",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        help="A CSV list of users to be added.",
    ),
    group_csv: Path | None = typer.Option(
        None,
        "--group-csv",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        help="A CSV list of groups to be updated.",
    ),
) -> None:
    """
Add a single user to a single user group. Alternatively, any number of \
users can be added to any number of groups by utilizing csv files.
    """

    async def fetch_data() -> tuple[dict[str, User], dict[str, Group]]:
        _users, _groups = await asyncio.gather(
            usr_api.list_users([]),
            grp_api.list_groups([]),
        )
        return {user.id: user for user in _users}, {
            group.id: group for group in _groups
        }

    async def context_wrapper(group: Group, user: User) -> tuple[Group, User]:
        try:
            await grp_api.add_group_member(group.id, user.id)
        except HTTPError as e:
            raise MemberChangeError(group, user, e) from e
        return group, user

    async def run_tasks(groups: list[Group], users: list[User]) -> None:
        task_id = add_task(
            f"Adding {len(users)} users to {len(groups)} groups",
            total=len(users) * len(groups),
        )
        tasks = [
            context_wrapper(group, user) for group in groups for user in users
        ]
        for task in asyncio.as_completed(tasks):
            try:
                group, user = await task
                print_result(f"Adding {user.email} to {group.name}", True)
            except MemberChangeError as e:
                print_result(f"Adding {e.user.email} to {e.group.name}", False)
                print_error(str(e))
            finally:
                update_task(task_id, advance=1)

    with progress_context():
        user_dict, group_dict = asyncio.run(fetch_data())
    group_id = resolve_optional_argument(group_id)
    groups = resolve_groups(group_id, group_name, group_csv, group_dict)
    users = resolve_users(user_id, email, user_csv, user_dict)
    member_presenter.print_change_confirmation(users, groups, "Add")
    typer.confirm(
        f"The {len(users) * len(groups)} changes listed above are "
        "pending. Do you wish to proceed?"
    )
    with progress_context():
        asyncio.run(run_tasks(groups, users))
