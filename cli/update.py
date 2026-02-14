import subprocess
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import httpx
import typer
from packaging import version
from rich.console import Console
from rich.panel import Panel

PROJECT_FILE = Path(__file__).parent.parent / "pyproject.toml"


console = Console()
app = typer.Typer(help="Update jam to the latest version")


@dataclass
class Release:
    version: str
    download_url: str
    release_notes_url: str


def get_project_settings() -> dict[str, Any]:
    with open(PROJECT_FILE, "rb") as file:
        return tomllib.load(file)


def get_latest_release(url: str) -> Release:
    response = httpx.get(url, timeout=10, follow_redirects=True)
    response.raise_for_status()
    data = response.json()
    latest_version = data["tag_name"].lstrip("v")
    release_notes_url = data["html_url"]
    for asset in data.get("assets", []):
        if asset["name"].endswith(".whl") or asset["name"].endswith(".tar.gz"):
            download_url = asset["browser_download_url"]
            break
    return Release(version=latest_version, download_url=download_url, release_notes_url=release_notes_url)


@app.command(name="check")
def check_update(quiet: bool = typer.Option(False, "-q", "--quiet", help="Only show if update is available.")) -> None:
    config = get_project_settings()
    current = config["project"]["version"]
    if not quiet:
        console.print(f"Current version: {current}")
        console.print("Checking for updates...")
    latest = get_latest_release(f"{config['project']['urls']['Repository']}/releases/latest")
    if version.parse(latest.version) > version.parse(current):
        console.print(Panel(
            f"[green]New version available:[/green] [bold]{latest}[/bold]\n"
            f"[cyan]Release Notes:[/cyan] {latest.release_notes_url}\n"
            "Run [bold]jam update install[/bold] to update",
            title="Update Available",
            border_style="green",
        ))
    else:
        if not quiet:
            console.print("[green] You are on the latest version.[/green]")


@app.command(name="install")
def install_update(force: bool = typer.Option(False, "-f", "--force", help="Force install even if on latest version.")) -> None:
    config = get_project_settings()
    current = config["project"]["version"]
    console.print(f"[cyan]Current version:[/cyan] {current}")
    latest = get_latest_release(f"{config['project']['urls']['Repository']}/releases/latest")
    if not force and not version.parse(latest.version) > version.parse(current):
        console.print("[green]Already on the latest version.[/green]")
        console.print(f"Use [bold]--force[/bold] to reinstall version {latest.version}")
        raise typer.Exit(0)
    console.print(f"[green]Latest version:[/green] {latest.version}")
    console.print(f"[dim]Release notes: {latest.release_notes_url}[/dim]\n")
    if not force:
        confirm = typer.confirm("Do you wish to proceed with the update?")
        if not confirm:
            console.print("Update cancelled.")
            raise typer.Exit(0)
    console.print(f"[yellow]Installing version {latest.version}...[/yellow]")
    try:
        subprocess.run(
            ["uv", "tool", "install", "--force", "--from", latest.download_url, "jam-jumpcloud"],
            check=True,
            capture_output=True,
            text=True,
        )
        console.print(f"[green]Successfully updated to version {latest.version}[/green]")
        console.print(f"[dim]Release notes: {latest.release_notes_url}[/dim]")
    except subprocess.CalledProcessError as e:
        console.print(f"[red]Update failed:[/red] {e.stderr}\n")
        console.print("[yellow]Try updating manually:[/yellow]")
        console.print(f" uv tool install --force {latest.download_url}")
        raise typer.Exit(1)
    except FileNotFoundError:
        console.print("[red]Error: 'uv' command not found[/red]")
        console.print("Install uv: https://github.com/astral-sh/uv")
        raise typer.Exit(1)
