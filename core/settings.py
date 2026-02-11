from functools import lru_cache
from typing import Tuple, Type

from pydantic import Field
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    PyprojectTomlConfigSettingsSource,
    SettingsConfigDict,
)


class Settings(BaseSettings):
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
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            env_settings,
            dotenv_settings,
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
