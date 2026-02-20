import os
from functools import lru_cache
from pathlib import Path
from typing import Any

from pydantic import Field
from pydantic.fields import FieldInfo
from pydantic_settings import (
    BaseSettings,
    DotEnvSettingsSource,
    JsonConfigSettingsSource,
    PydanticBaseSettingsSource,
    PyprojectTomlConfigSettingsSource,
    SettingsConfigDict,
)

from core.config import init_config


class JamConfigSource(JsonConfigSettingsSource):
    def __init__(self, settings_cls: type[BaseSettings]) -> None:
        config_path = init_config()
        super().__init__(settings_cls, config_path)

    def get_field_value(
        self,
        field: FieldInfo,  # noqa: ARG002
        field_name: str,
    ) -> tuple[Any, str, bool]:
        json_data = self._read_files(self.json_file_path)
        jam_config = json_data.get("jam", {})
        if field_name in jam_config:
            return jam_config[field_name], field_name, False
        return None, field_name, False


class Settings(BaseSettings):
    JAM_CONFIG_PATH: Path = Field(
        default_factory=lambda: Path(
            os.environ.get(
                "JAM_CONFIG_PATH", str(Path.home() / ".config" / "jam")
            )
        )
    )
    JAM_CLIENT_ID: str = Field(default="")
    JAM_CLIENT_SECRET: str = Field(default="")
    api_url: str = Field(default="https://console.jumpcloud.com/api")
    oauth_url: str = Field(
        default="https://admin-oauth.id.jumpcloud.com/oauth2/token"
    )
    timeout: int = Field(default=10)
    limit: int = Field(default=100)
    local_tz: str = Field(default="US/Eastern")
    console_user_fields: dict[str, str] = Field(default_factory=dict)
    csv_user_fields: dict[str, str] = Field(default_factory=dict)
    console_system_fields: dict[str, str] = Field(default_factory=dict)
    csv_system_fields: dict[str, str] = Field(default_factory=dict)
    console_group_fields: dict[str, str] = Field(default_factory=dict)
    csv_group_fields: dict[str, str] = Field(default_factory=dict)
    model_config = SettingsConfigDict(
        env_file=Path(
            os.environ.get(
                "JAM_CONFIG_PATH", str(Path.home() / ".config" / "jam")
            )
        )
        / ".env",
        pyproject_toml_table_header=("tool", "jam"),
        extra="ignore",
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,  # noqa: ARG003
        file_secret_settings: PydanticBaseSettingsSource,  # noqa: ARG003
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        config_path = Path(
            os.environ.get(
                "JAM_CONFIG_PATH", str(Path.home() / ".config" / "jam")
            )
        )
        custom_dotenv = DotEnvSettingsSource(
            settings_cls,
            env_file=config_path / ".env",
        )
        return (
            init_settings,
            env_settings,
            custom_dotenv,
            JamConfigSource(settings_cls),
            PyprojectTomlConfigSettingsSource(settings_cls),
        )

    @property
    def client_id(self) -> str:
        return self.JAM_CLIENT_ID

    @property
    def client_secret(self) -> str:
        return self.JAM_CLIENT_SECRET


@lru_cache
def get_settings() -> Settings:
    """Return a cached singleton instance of Settings."""
    return Settings()
