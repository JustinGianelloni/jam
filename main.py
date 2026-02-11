import importlib

import typer

MODULES = ["users", "systems"]


def main() -> None:
    app = typer.Typer()
    for module in MODULES:
        cmd = importlib.import_module(f"cli.{module}.commands")
        app.add_typer(cmd.app, name=module)
    app()


if __name__ == "__main__":
    main()
