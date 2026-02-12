from api import users as api
from cli.output import (
    CONSOLE,
    create_table,
    print_json,
    print_table,
    print_value,
    save_to_csv,
)
from core.client import get_client
from core.settings import get_settings


def _get_settings():
    return get_settings()


def _get_user_table(title: str):
    return create_table(
        title, list(_get_settings().console_user_fields.keys())
    )


def _add_user_rows(table, users: list) -> None:
    settings = _get_settings()
    for user in users:
        row_values = [
            getattr(user, attr)
            for attr in settings.console_user_fields.values()
        ]
        table.add_row(*row_values)


def get_user(user_id: str, json: bool) -> None:
    """Get and display a single user."""
    user = api.get_user(get_client(), user_id)
    if json:
        print_json(user)
        return
    table = _get_user_table("System User")
    _add_user_rows(table, [user])
    print_table(table)


def list_users(filters: list[str] | None, csv_file: str | None) -> None:
    """List and display all users matching filters."""
    users = api.list_users(get_client(), filters)
    table = _get_user_table("System Users")
    _add_user_rows(table, users)
    print_table(table)
    if csv_file:
        save_to_csv(users, csv_file, _get_settings().csv_user_fields)


def find_user(email: str) -> None:
    """Find users by email address."""
    users = api.find_user(get_client(), email)
    if not users:
        CONSOLE.print(f"No users found with email address matching '{email}'.")
        return
    if len(users) == 1:
        print_value(users[0].id)
        return
    table = _get_user_table("Search Results")
    _add_user_rows(table, users)
    print_table(table)


def list_bound_systems(user_id: str) -> None:
    """List all systems bound to a user."""
    systems = api.list_bound_systems(get_client(), user_id)
    if not systems:
        CONSOLE.print(f"No devices found bound to user with ID '{user_id}'.")
        return
    if len(systems) == 1:
        print_value(systems[0])
        return
    table = create_table("Bound Systems", ["ID"])
    for system in systems:
        table.add_row(system)
    print_table(table)
