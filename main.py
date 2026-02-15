import importlib
from pathlib import Path

import typer

from cli.config import app as config_app


def discover_modules() -> list[str]:
    cli_path = Path(__file__).parent / "cli"
    modules = [
        item.name
        for item in cli_path.iterdir()
        if item.is_dir()
        and not item.name.startswith("_")
        and (item / "commands.py").exists()
    ]
    return sorted(modules)


def main() -> None:
    app = typer.Typer(
        help="JumpCloud CLI - \
        Manage JumpCloud resources from the command line",
    )
    for module in discover_modules():
        cmd = importlib.import_module(f"cli.{module}.commands")
        app.add_typer(cmd.app, name=module)
    app.add_typer(config_app, name="config")
    app()


if __name__ == "__main__":
    main()
