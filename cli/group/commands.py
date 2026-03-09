import asyncio

import typer

from api import groups as grp_api
from api.groups import GroupNotFoundError, NoGroupsFoundError
from cli.group import presenter
from cli.group.member.commands import app as member_app
from cli.input import resolve_optional_list_argument
from cli.output import print_error, save_to_csv
from core.progress import progress_context
from core.settings import get_settings

SETTINGS = get_settings()
app = typer.Typer()

app.add_typer(member_app, name="member")


@app.command(name="list")
def list_user_groups(
    csv_file: str | None = typer.Option(
        None,
        "--csv",
        help="Export result to specified CSV file.",
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
    """
    try:
        with progress_context():
            groups = asyncio.run(grp_api.list_groups([]))
    except NoGroupsFoundError as e:
        print_error(f"No groups found with the provided filters: {e.filters}")
        raise typer.Exit(1) from e
    presenter.print_groups(groups, json)
    if csv_file:
        save_to_csv(groups, csv_file, SETTINGS.csv_group_fields)


@app.command(name="get")
def get_user_groups(
    group_ids: list[str] | None = typer.Argument(
        None,
        help="One or more valid JumpCloud group IDs.",
    ),
    name: str | None = typer.Option(
        None,
        "-n",
        "--name",
        help="A partial or exact name for a JumpCloud group.",
    ),
    csv_file: str | None = typer.Option(
        None,
        "--csv",
        help="Export result to specified CSV file.",
    ),
    json: bool = typer.Option(
        False,
        "-j",
        "--json",
        is_flag=True,
        help="Return a full json model of the user group(s)."
    ),
) -> None:
    """
Look up user groups by IDs or a name search.
    """
    group_ids = resolve_optional_list_argument(group_ids)
    if group_ids and name:
        msg = "Too many arguments specified. Use 'jam group get --help' for details."
        raise typer.BadParameter(msg)
    if not group_ids and not name:
        msg = "No arguments specified. Use 'jam group get --help' for details."
        raise typer.BadParameter(msg)
    if name:
        try:
            with progress_context():
                groups = asyncio.run(grp_api.list_groups([f"name:search:{name}"]))
        except NoGroupsFoundError as e:
            print_error(f"No groups found with the provided filters: {e.filters}")
            raise typer.Exit(1) from e
    elif group_ids:
        try:
            with progress_context():
                groups = asyncio.run(grp_api.get_groups(group_ids))
        except GroupNotFoundError as e:
            print_error(f"No group found with ID '{e.group_id}'")
            raise typer.Exit(1) from e
    presenter.print_groups(groups, json)
    if csv_file:
        save_to_csv(groups, csv_file, SETTINGS.csv_group_fields)
