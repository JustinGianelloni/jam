import os
from functools import lru_cache
from pathlib import Path
from typing import Any

from pydantic import Field
from pydantic.fields import FieldInfo
from pydantic_settings import (
    BaseSettings,
    JsonConfigSettingsSource,
    PydanticBaseSettingsSource,
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
    JAM_CLIENT_ID: str = Field(init=False)
    JAM_CLIENT_SECRET: str = Field(init=False)
    api_url: str = Field(init=False)
    oauth_url: str = Field(init=False)
    timeout: int = Field(init=False)
    limit: int = Field(init=False)
    local_tz: str = Field(init=False)
    console_user_fields: dict[str, str] = Field(init=False)
    csv_user_fields: dict[str, str] = Field(init=False)
    console_system_fields: dict[str, str] = Field(init=False)
    csv_system_fields: dict[str, str] = Field(init=False)
    model_config = SettingsConfigDict(
        env_file=".env",
        pyproject_toml_table_header=("tool", "jam"),
        extra="ignore",
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,  # noqa: ARG003
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            JamConfigSource(settings_cls),
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
