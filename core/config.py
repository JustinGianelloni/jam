from pathlib import Path
from typing import Any

import tomlkit
from rich.console import Console

console = Console()

def get_config_dir() -> Path:
    config_dir = Path.home() / ".config" / "jam"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def get_config_path() -> Path:
    return get_config_dir() / "config.toml"


def get_default_config() -> dict[str, Any]:
    return {
        "jam": {
            "api_url": "https://console.jumpcloud.com/api",
            "oauth_url": "https://admin-oauth.id.jumpcloud.com/oauth2/token",
            "timeout": 10,
            "limit": 100,
            "local_tz": "US/Eastern",
            "console_user_fields": {
                "ID": "id",
                "State": "pretty_state",
                "Email": "email",
                "Employee Type": "employee_type",
                "Job Title": "job_title",
                "Department": "department",
            },
            "csv_user_fields": {
                "ID": "id",
                "State": "state",
                "Email": "email",
                "Employee Type": "employee_type",
                "Job Title": "job_title",
                "Department": "department",
                "Cost Center": "cost_center",
            },
            "console_system_fields": {
                "ID": "id",
                "Hostname": "hostname",
                "Last Contact (Local)": "pretty_last_contact",
                "OS": "pretty_os",
                "Serial": "serial_number",
            },
            "csv_system_fields": {
                "ID": "id",
                "Hostname": "hostname",
                "Last Contact": "last_contact",
                "OS": "os",
                "Serial": "serial_number",
            },
        }
    }


def init_config() -> Path:
    config_path = get_config_path()
    if not config_path.exists():
        default_config = get_default_config()
        with open(config_path, "w") as file:
            tomlkit.dump(default_config, file)
        console.print(f"Created default configuration at: {config_path}")
    return config_path


def load_config() -> dict[str, Any]:
    config_path = init_config()
    with open(config_path, "r") as file:
        return tomlkit.load(file)
