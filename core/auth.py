import atexit
import httpx

from httpx import Response
from pathlib import Path
from pydantic import BaseModel, ValidationError
from datetime import datetime, timedelta
from core.settings import Settings
from typing import Any
from base64 import b64encode
from pytz import utc

TOKEN_FILE: Path = Path("token.json")
SETTINGS: Settings = Settings()


class TokenState(BaseModel):
    access_token: str | None = None
    expires_at: datetime | None = None


class TokenFactory:
    def __init__(self) -> None:
        self._state = self._load()
        atexit.register(self._save)

    def _load(self) -> TokenState:
        try:
            with open(TOKEN_FILE, "r") as file:
                return TokenState.model_validate_json(file.read())
        except ValidationError or FileNotFoundError:
            return TokenState()

    def _save(self) -> None:
        with open(TOKEN_FILE, "w") as file:
            file.write(self._state.model_dump_json(indent=2))

    def _request_token(self) -> None:
        creds: str = b64encode(
            f"{SETTINGS.CLIENT_ID}:{SETTINGS.CLIENT_SECRET}".encode()
        ).decode()
        headers: dict[str, Any] = {
            "Accept": "application/json",
            "Authorization": f"Basic {creds}",
        }
        params: dict[str, Any] = {
            "scope": "api",
            "grant_type": "client_credentials",
        }
        response: Response = httpx.post(
            SETTINGS.JUMPCLOUD_OAUTH_URL,
            headers=headers,
            params=params,
            timeout=SETTINGS.TIMEOUT,
        )
        response.raise_for_status()
        body: dict[str, Any] = response.json()
        self._state.access_token = body["access_token"]
        self._state.expires_at = datetime.now(tz=utc) + timedelta(
            seconds=body["expires_in"]
        )

    def get_token(self) -> str:
        if (
            self._state.expires_at is None
            or self._state.expires_at < datetime.now(tz=utc)
        ):
            self._request_token()
        return f"Bearer {self._state.access_token}"
