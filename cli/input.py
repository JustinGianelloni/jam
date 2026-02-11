import sys

import typer


def resolve_argument(value: str | None, param_name: str) -> str:
    """
    Resolve an argument from direct input or stdin.

    Args:
        value: The value passed as a CLI argument, or None.
        param_name: The name of the parameter (for error messages).

    Returns:
        The resolved value from either the argument or stdin.

    Raises:
        typer.BadParameter: If no value is provided and stdin is empty.
    """
    if value:
        return value
    if not sys.stdin.isatty():
        stdin_value = sys.stdin.read().strip()
        if stdin_value:
            return stdin_value
    raise typer.BadParameter(f"{param_name} not provided")


def resolve_optional_argument(value: str | None) -> str | None:
    """
    Resolve an optional argument from direct input or stdin.

    Args:
        value: The value passed as a CLI argument, or None.

    Returns:
        The resolved value, or None if not provided.
    """
    if value:
        return value
    if not sys.stdin.isatty():
        stdin_value = sys.stdin.read().strip()
        if stdin_value:
            return stdin_value
    return None


def resolve_list_argument(values: list[str] | None) -> list[str]:
    """
    Resolve a list argument from direct input or stdin.

    Stdin input is split by newlines to support multiple values.

    Args:
        values: The values passed as CLI arguments, or None.

    Returns:
        The resolved list of values.
    """
    if values:
        return values
    if not sys.stdin.isatty():
        stdin_value = sys.stdin.read().strip()
        if stdin_value:
            return stdin_value.split("\n")
    return []
