from httpx import Client
from rich.progress import Progress

from core.settings import Settings
from models.system_user import MFA, SystemUser

SETTINGS: Settings = Settings()


def list_all_system_users(client: Client, filters: list[str] | None) -> list[SystemUser]:
    endpoint = "/systemusers"
    params = {"skip": 0, "limit": SETTINGS.limit, "sort": "_id"}
    if filters:
        for i, f in enumerate(filters):
            params[f"filter[{i}]"] = f
    system_users: list[SystemUser] = []
    total: int | None = None
    with Progress() as progress:
        task = progress.add_task("Fetching users from JumpCloud", total=None)
        while total is None or params["skip"] < total:
            response = client.get(endpoint, params=params)
            response.raise_for_status()
            body = response.json()
            if total is None:
                total = body.get("totalCount", 0)
                progress.update(task, total=total)
            system_users.extend(
                [SystemUser(**result) for result in body.get("results")]
            )
            params["skip"] += SETTINGS.limit
            progress.update(task, completed=params["skip"])
    return system_users


def list_system_user(client: Client, user_id: str) -> SystemUser:
    endpoint = f"/systemusers/{user_id}"
    response = client.get(endpoint)
    response.raise_for_status()
    return SystemUser(**response.json())


def update_system_user(client: Client, user: SystemUser) -> SystemUser:
    endpoint = f"/systemusers/{user.id}"
    data = user.model_dump(mode="json")
    response = client.put(endpoint, data=data)
    response.raise_for_status()
    return SystemUser(**response.json())


def expire_system_users_password(client: Client, user_id: str) -> None:
    endpoint = f"/systemusers/{user_id}/expire"
    response = client.post(endpoint)
    response.raise_for_status()


def update_system_users_mfa_properties(
    client: Client, user_id: str, enabled: bool, mfa: MFA
) -> None:
    endpoint = f"/systemusers/{user_id}/mfa/enforce"
    data = {
        "enable_user_portal_multifactor": enabled,
        "mfa": mfa,
    }
    response = client.post(endpoint, data=data)
    response.raise_for_status()


def sync_system_users_mfa_enrollment_status(
    client: Client, user_id: str
) -> None:
    endpoint = f"/systemusers/{user_id}/mfasync"
    response = client.post(endpoint)
    response.raise_for_status()


def force_set_system_users_password(
    client: Client, user_id: str, password: str
) -> None:
    endpoint = f"/systemusers/{user_id}/password"
    data = {
        "password": password,
    }
    response = client.post(endpoint, data=data)
    response.raise_for_status()


def reactivate_system_user(client: Client, user_id: str) -> None:
    endpoint = f"/systemusers/{user_id}/reactivate"
    response = client.post(endpoint)
    response.raise_for_status()


def reset_system_users_mfa_token(
    client: Client, user_id: str, mfa: MFA
) -> None:
    endpoint = f"/systemusers/{user_id}/resetmfa"
    data = mfa.model_dump(mode="json", exclude={"configured"})
    response = client.post(endpoint, data=data)
    response.raise_for_status()


def activate_system_user(client: Client, user_id: str) -> None:
    endpoint = f"/systemusers/{user_id}/activate"
    response = client.post(endpoint)
    response.raise_for_status()


def suspend_system_user(client: Client, user_id: str) -> None:
    endpoint = f"/systemusers/{user_id}/state/suspend"
    response = client.post(endpoint)
    response.raise_for_status()


def unlock_system_user(client: Client, user_id: str) -> None:
    endpoint = f"/systemusers/{user_id}/unlock"
    response = client.post(endpoint)
    response.raise_for_status()


def find_system_user(client: Client, email: str) -> str:
    endpoint = "/search/systemusers"
    data = {
        "searchFilter": {
            "searchTerm": email,
            "fields": ["email"],
        },
        "fields": "_id",
    }
    response = client.post(endpoint, json=data)
    response.raise_for_status()
    body = response.json()
    if body.get("totalCount") == 0:
        raise ValueError(f"No user found with email: {email}")
    elif body.get("totalCount") > 1:
        raise ValueError(f"More than one user found with email: {email}")
    return body.get("results")[0].get("_id")
