import asyncio

import typer

from api import applications as app_api
from cli.application import presenter as app_presenter
from cli.application.group.commands import app as group_app
from cli.output import save_to_csv
from core.progress import progress_context
from core.settings import get_settings

SETTINGS = get_settings()
app = typer.Typer()

app.add_typer(group_app, name="group")


@app.command(name="list")
def list_applications(
    filters: list[str] | None = typer.Option(
        None,
        "--filter",
        help="Any number of filters using JumpCloud's filter syntax, e.g. "
        "'name:$eq:GitHub Prod'",
    ),
    csv_file: str | None = typer.Option(
        None,
        "--csv",
        help="Export result to specified CSV file",
    ),
    name: str | None = typer.Option(
        None,
        "--name",
        help="Filter applications by their name, e.g. 'GitHub Prod'",
    ),
    json: bool = typer.Option(
        False,
        "-j",
        "--json",
        is_flag=True,
        help="Return a full JSON model of the user applications",
    ),
    active: bool = typer.Option(
        None,
        "-a",
        "--active",
        is_flag=True,
        help="Filter applications to only show active applications.",
    ),
    inactive: bool = typer.Option(
        None,
        "-i",
        "--inactive",
        is_flag=True,
        help="Filter application to only show inactive applications",
    ),
) -> None:
    """
List all applications in JumpCloud.
Applications can be filtered by specifying a flag with a value or by using \
JumpCloud's filter syntax.
"""
    if not filters:
        filters = []
    if name:
        filters.append(f"displayLabel:$sw:{name}")
    if active:
        filters.append("active:$eq:true")
    if inactive:
        filters.append("active:$eq:false")
    with progress_context():
        apps = asyncio.run(app_api.list_applications(filters))
    app_presenter.print_applications(apps, json)
    if csv_file:
        save_to_csv(apps, csv_file, SETTINGS.csv_app_fields)
