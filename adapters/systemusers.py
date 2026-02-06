from httpx import AsyncClient
from models.SystemUsers import SystemUser, MFA
from core.settings import Settings

SETTINGS: Settings = Settings()


async def list_all_system_users(
    client: AsyncClient, filters: list[str]
) -> list[SystemUser]:
    endpoint = "/systemusers"
    params = {"skip": 0, "limit": SETTINGS.LIMIT, "sort": "_id"}
    if filters:
        for i, f in enumerate(filters):
            params[f"filter[{i}]"] = f
    system_users: list[SystemUser] = []
    while (response := await client.get(endpoint, params=params)).json().get(
        "totalCount", 0
    ) > params["skip"]:
        response.raise_for_status()
        system_users.extend(
            [SystemUser(**result) for result in response.json().get("results")]
        )
        params["skip"] += SETTINGS.LIMIT
    return system_users


async def list_system_user(client: AsyncClient, user_id: str) -> SystemUser:
    endpoint = f"/systemusers/{user_id}"
    response = await client.get(endpoint)
    response.raise_for_status()
    return SystemUser(**response.json())


async def update_system_user(
    client: AsyncClient, user: SystemUser
) -> SystemUser:
    endpoint = f"/systemusers/{user.id}"
    data = user.model_dump(mode="json")
    response = await client.put(endpoint, data=data)
    response.raise_for_status()
    return SystemUser(**response.json())


async def expire_system_users_password(
    client: AsyncClient, user_id: str
) -> None:
    endpoint = f"/systemusers/{user_id}/expire"
    response = await client.post(endpoint)
    response.raise_for_status()


async def update_system_users_mfa_properties(
    client: AsyncClient, user_id: str, enabled: bool, mfa: MFA
) -> None:
    endpoint = f"/systemusers/{user_id}/mfa/enforce"
    data = {
        "enable_user_portal_multifactor": enabled,
        "mfa": mfa,
    }
    response = await client.post(endpoint, data=data)
    response.raise_for_status()


async def sync_system_users_mfa_enrollment_status(
    client: AsyncClient, user_id: str
) -> None:
    endpoint = f"/systemusers/{user_id}/mfasync"
    response = await client.post(endpoint)
    response.raise_for_status()


async def force_set_system_users_password(
    client: AsyncClient, user_id: str, password: str
) -> None:
    endpoint = f"/systemusers/{user_id}/password"
    data = {
        "password": password,
    }
    response = await client.post(endpoint, data=data)
    response.raise_for_status()


async def reactivate_system_user(client: AsyncClient, user_id: str) -> None:
    endpoint = f"/systemusers/{user_id}/reactivate"
    response = await client.post(endpoint)
    response.raise_for_status()


async def reset_system_users_mfa_token(
    client: AsyncClient, user_id: str, mfa: MFA
) -> None:
    endpoint = f"/systemusers/{user_id}/resetmfa"
    data = mfa.model_dump(mode="json", exclude={"configured"})
    response = await client.post(endpoint, data=data)
    response.raise_for_status()


async def activate_system_user(client: AsyncClient, user_id: str) -> None:
    endpoint = f"/systemusers/{user_id}/activate"
    response = await client.post(endpoint)
    response.raise_for_status()


async def suspend_system_user(client: AsyncClient, user_id: str) -> None:
    endpoint = f"/systemusers/{user_id}/state/suspend"
    response = await client.post(endpoint)
    response.raise_for_status()


async def unlock_system_user(client: AsyncClient, user_id: str) -> None:
    endpoint = f"/systemusers/{user_id}/unlock"
    response = await client.post(endpoint)
    response.raise_for_status()
