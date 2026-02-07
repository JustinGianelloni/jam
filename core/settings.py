from typing import Tuple, Type

from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    PyprojectTomlConfigSettingsSource,
    SettingsConfigDict,
)


class Settings(BaseSettings):
    JAM_CLIENT_ID: str
    JAM_CLIENT_SECRET: str
    api_url: str
    oauth_url: str
    timeout: int
    limit: int
    local_tz: str
    console_user_fields: dict[str, str]
    csv_user_fields: dict[str, str]
    console_system_fields: dict[str, str]
    csv_system_fields: dict[str, str]
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
