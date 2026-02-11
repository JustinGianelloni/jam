import json
from csv import DictWriter
from pathlib import Path
from typing import Any, Sequence

from pydantic import BaseModel
from rich.console import Console
from rich.table import Table

CONSOLE = Console()
OUTPUT_DIR = Path(__file__).parent.parent / "output"


def create_table(title: str, columns: Sequence[str]) -> Table:
    table = Table(title=title)
    for column in columns:
        table.add_column(column)
    return table


def print_table(table: Table) -> None:
    CONSOLE.print(table)


def print_value(value: Any) -> None:
    CONSOLE.print(value)


def print_json(model: BaseModel) -> None:
    CONSOLE.print(model.model_dump(mode="json", exclude_none=True))


def save_to_csv(
    items: Sequence[BaseModel],
    filename: str,
    field_mapping: dict[str, str],
) -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    file_path = OUTPUT_DIR / filename
    fieldnames = list(field_mapping.values())
    with open(file_path, "w") as file:
        writer = DictWriter(file, fieldnames=fieldnames)
        # Write header row with display names
        writer.writerow({v: k for k, v in field_mapping.items()})
        writer.writerows(
            [item.model_dump(include=set(fieldnames)) for item in items]
        )
    CONSOLE.print(f"Exported {len(items)} items to '{file_path}'.")


def save_to_json(model: BaseModel, filename: str) -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    file_path = OUTPUT_DIR / filename
    with open(file_path, "w") as file:
        json.dump(
            model.model_dump(mode="json", exclude_none=True), file, indent=2
        )
    CONSOLE.print(f"Exported to '{file_path}'.")
