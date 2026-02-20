import json
import sys
from collections.abc import Sequence
from csv import DictWriter
from pathlib import Path
from typing import Any

from pydantic import BaseModel
from rich.console import Console
from rich.table import Table

CONSOLE = Console()
OUTPUT_DIR = Path(__file__).parent.parent / "output"


def is_piped() -> bool:
    return not sys.stdout.isatty()


def create_table(title: str, columns: Sequence[str]) -> Table:
    table = Table(title=title)
    for column in columns:
        table.add_column(column)
    return table


def print_table(table: Table) -> None:
    CONSOLE.print(table)


def print_values(values: list[Any]) -> None:
    print("\n".join(values))  # noqa: T201


def print_json(models: Sequence[BaseModel]) -> None:
    if not models:
        output = "No results match your query."
    elif len(models) == 1:
        output = json.dumps(
            models[0].model_dump(mode="json", exclude_none=True),
            indent=2,
        )
    else:
        output = [
            json.dumps(m.model_dump(mode="json", exclude_none=True))
            for m in models
        ]
    if is_piped():
        print(output)  # noqa: T201
    else:
        CONSOLE.print(output)


def save_to_csv(
    items: Sequence[BaseModel],
    filename: str,
    field_mapping: dict[str, str],
) -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    file_path = OUTPUT_DIR / filename
    fieldnames = list(field_mapping.values())
    with Path.open(file_path, "w") as file:
        writer = DictWriter(file, fieldnames=fieldnames)
        # Write header row with display names
        writer.writerow({v: k for k, v in field_mapping.items()})
        writer.writerows(
            [item.model_dump(include=set(fieldnames)) for item in items],
        )
    CONSOLE.print(f"Exported {len(items)} items to '{file_path}'.")
