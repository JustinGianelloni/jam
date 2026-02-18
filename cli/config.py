from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

from core.config import get_config_path, init_config

app = typer.Typer(help="Manage jam configuration")
console = Console()


@app.command(name="path")
def show_path() -> None:
    config_path = get_config_path()
    console.print(f"[cyan]Configuration file:[/cyan] {config_path}")
    if config_path.exists():
        console.print("[green]File exists[/green]")
    else:
        console.print(
            "[yellow]File doesn't exist yet and will be created on "
            "first run[/yellow]",
        )


@app.command(name="show")
def show_config() -> None:
    config_path = init_config()
    with Path.open(config_path) as file:
        config = file.read()
    console.print(
        Panel(
            Syntax(config, "toml", line_numbers=True),
            title=f"Configuration: {config_path}",
        ),
    )


@app.command(name="reset")
def reset_config(
    force: bool = typer.Option(
        False,
        "-f",
        "--force",
        help="Skip confirmation",
    ),
) -> None:
    config_path = get_config_path()
    if not force:
        console.print(
            "[yellow]This will reset your configuration to defaults.[/yellow]",
        )
        console.print(f"[dim]Location: {config_path}[/dim]\n")
        if not typer.confirm("Are you sure?"):
            console.print("Reset cancelled.")
            raise typer.Exit(0)
        if config_path.exists():
            backup_path = config_path.with_suffix(".toml.backup")
            config_path.rename(backup_path)
            console.print(
                f"[dim]Backed up existing config to: {backup_path}[/dim]",
            )
        init_config()
        console.print("[green]Configuration reset to defaults.[/green]")
