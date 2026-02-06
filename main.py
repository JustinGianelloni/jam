from httpx import AsyncClient
from core.auth import TokenFactory
from typing import Any
from core.settings import Settings

TOKEN_FACTORY: TokenFactory = TokenFactory()
SETTINGS: Settings = Settings()


def get_client() -> AsyncClient:
    headers: dict[str, Any] = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": TOKEN_FACTORY.get_token(),
    }
    return AsyncClient(
        base_url=SETTINGS.JUMPCLOUD_API_URL,
        headers=headers,
        timeout=SETTINGS.TIMEOUT,
    )


def main():
    settings = Settings()


if __name__ == "__main__":
    main()
