import asyncio

import typer

from api import groups as grp_api
from cli.group import presenter
from cli.group.member.commands import app as member_app
from cli.output import save_to_csv
from core.settings import get_settings

SETTINGS = get_settings()
app = typer.Typer()

app.add_typer(member_app, name="member")

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
