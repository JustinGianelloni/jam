import atexit
from base64 import b64encode
from datetime import datetime, timedelta
from functools import lru_cache
from pathlib import Path
from typing import Any

import httpx
from httpx import AsyncClient, Response
from pydantic import BaseModel
from pytz import utc

from core.settings import get_settings

SETTINGS = get_settings()
CONFIG_PATH = Path(SETTINGS.JAM_CONFIG_PATH)
TOKEN_FILE = CONFIG_PATH / "token.json"


class TokenState(BaseModel):
    access_token: str | None = None
    expires_at: datetime | None = None


class TokenFactory:
    def __init__(self) -> None:
        self._state = self._load()
        atexit.register(self._save)

    def _load(self) -> TokenState:
        try:
            with Path.open(TOKEN_FILE, "r") as file:
                return TokenState.model_validate_json(file.read())
        except FileNotFoundError:
            return TokenState()

    def _save(self) -> None:
        with Path.open(TOKEN_FILE, "w") as file:
            file.write(self._state.model_dump_json(indent=2))

    def _request_token(self) -> None:
        creds: str = b64encode(
            f"{SETTINGS.client_id}:{SETTINGS.client_secret}".encode(),
        ).decode()
        headers: dict[str, Any] = {
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {creds}",
        }
        data: dict[str, Any] = {
            "scope": "api",
            "grant_type": "client_credentials",
        }
        response: Response = httpx.post(
            SETTINGS.oauth_url,
            headers=headers,
            data=data,
            timeout=SETTINGS.timeout,
        )
        response.raise_for_status()
        body: dict[str, Any] = response.json()
        self._state.access_token = body["access_token"]
        self._state.expires_at = datetime.now(tz=utc) + timedelta(
            seconds=body["expires_in"],
        )

    def get_token(self) -> str:
        if (
            self._state.expires_at is None
            or self._state.expires_at < datetime.now(tz=utc)
        ):
            self._request_token()
        return f"Bearer {self._state.access_token}"


@lru_cache
def get_token_factory() -> TokenFactory:
    return TokenFactory()


def get_client() -> AsyncClient:
    token_factory = get_token_factory()
    headers: dict[str, Any] = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": token_factory.get_token(),
    }
    return AsyncClient(
        base_url=SETTINGS.api_url,
        headers=headers,
        timeout=SETTINGS.timeout,
    )
