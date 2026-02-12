import typer

from cli.input import resolve_argument
from cli.systems import presenter

app = typer.Typer()


@app.command(name="list")
def list_systems(
    filters: list[str] | None = typer.Option(
        None,
        "--filter",
        help="Any number of filters using JumpCloud's filter syntax, e.g. 'osFamily:$eq:Windows'",
    ),
    csv_file: str | None = typer.Option(
        None, "--csv", help="Export result to specified CSV file"
    ),
    os: str | None = typer.Option(
        None,
        "--os",
        help="Filter systems by their operating system, e.g. 'Windows', 'Max OS X', or 'Ubuntu'",
    ),
    os_family: str | None = typer.Option(
        None,
        "--os-family",
        help="Filter systems by their operating system family, e.g. 'windows', 'darwin', or 'linux'",
    ),
) -> None:
    """
    List all systems in JumpCloud.
    Systems can be filtered by specifying a flag with a value or by using JumpCloud's filter syntax.
    For example, to filter for all Windows systems, you could use either '--os Windows' or '--filter os:$eq:Windows'.
    If both flag-based filters and filter syntax are used together, they will be combined into a single list of filters.
    """
    if not filters:
        filters = []
    if os:
        filters.append(f"os:$eq:{os}")
    if os_family:
        filters.append(f"osFamily:$eq:{os_family}")
    presenter.list_systems(filters, csv_file)


@app.command(name="get")
def get_system(
    system_id: str | None = typer.Argument(
        None,
        help="A valid UUID for a JumpCloud system, e.g. '69879fa9b5be2f2184d700da'",
    ),
    full: bool = typer.Option(
        False,
        "--full",
        is_flag=True,
        help="Display all available fields",
    ),
    json_file: str | None = typer.Option(
        None, "--json", help="Export system to specified JSON file"
    ),
) -> None:
    """
    Get a JumpCloud system by its UUID.
    """
    system_id = resolve_argument(system_id, "System ID")
    presenter.get_system(system_id, full, json_file)


@app.command(name="fde-key")
def fde_key(
    system_id: str | None = typer.Argument(
        None,
        help="A valid UUID for a JumpCloud system, e.g. '69879fa9b5be2f2184d700da'",
    ),
) -> None:
    """
    Returns the full disk encryption key for the specified system UUID.
    """
    system_id = resolve_argument(system_id, "System ID")
    presenter.get_fde_key(system_id)


@app.command(name="find")
def find_system(
    query: str | None = typer.Argument(
        None, help="A valid hostname our serial number for a JumpCloud system"
    ),
) -> None:
    """
    Find a JumpCloud system's UUID by its hostname or serial number. If the query returns multiple results, a table of matching systems will be displayed instead of a single UUID.
    """
    query = resolve_argument(query, "Hostname or serial number")
    presenter.find_system(query)


@app.command(name="bound-users")
def list_user_associations(
    system_id: str | None = typer.Argument(
        None,
        help="A valid UUID for a JumpCloud system, e.g. '69879fa9b5be2f2184d700da'",
    ),
) -> None:
    """
    Find all users bound to a system.
    """
    system_id = resolve_argument(system_id, "System ID")
    presenter.list_user_associations(system_id)