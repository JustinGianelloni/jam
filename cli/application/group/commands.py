import asyncio

import typer

from api import applications as app_api
from api import groups as grp_api
from cli.group import presenter as grp_presenter
from cli.input import resolve_argument
from cli.output import save_to_csv
from core.progress import progress_context
from core.settings import get_settings
from models.group import Group

SETTINGS = get_settings()
app = typer.Typer()


@app.command(name="list")
def list_groups(
    app_id: str | None = typer.Argument(
        None,
        help="A valid UUID for a JumpCloud application, e.g. "
        "'64dfcc79523de4972dce15f0'",
    ),
    json: bool = typer.Option(
        False,
        "-j",
        "--json",
        is_flag=True,
        help="Return a full JSON model of the groups.",
    ),
    csv_file: str | None = typer.Option(
        None,
        "--csv",
        help="Export result to specified CSV file",
    ),
) -> None:
    async def fetch_data(_app_id: str) -> tuple[list[str], dict[str, Group]]:
        _group_list, _all_groups = await asyncio.gather(
            app_api.list_associations(_app_id),
            grp_api.list_groups([]),
        )
        return _group_list, {group.id: group for group in _all_groups}

    app_id = resolve_argument(app_id, "Application ID")
    with progress_context():
        group_list, group_dict = asyncio.run(fetch_data(app_id))
    groups = [group_dict[group] for group in group_list]
    grp_presenter.print_groups(groups, json)
    if csv_file:
        save_to_csv(groups, csv_file, SETTINGS.csv_group_fields)
