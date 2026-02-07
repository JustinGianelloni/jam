from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

env_file: Path = Path.cwd() / Path(".env")

if not env_file.exists():
    raise FileNotFoundError("Missing '.env' file.")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=env_file)
    CLIENT_ID: str
    CLIENT_SECRET: str
    JUMPCLOUD_API_URL: str = "https://console.jumpcloud.com/api"
    JUMPCLOUD_OAUTH_URL: str = (
        "https://admin-oauth.id.jumpcloud.com/oauth2/token"
    )
    TIMEOUT: int = 10
    LIMIT: int = 100
    DEFAULT_CONSOLE_USER_FIELDS: dict[str, str] = {
        "ID": "id",
        "State": "pretty_state",
        "Email": "email",
        "Employee Type": "employee_type",
    }
    DEFAULT_CSV_USER_FIELDS: list[str] = [
        "id",
        "email",
        "state",
        "employee_type",
        "department",
        "cost_center",
    ]
