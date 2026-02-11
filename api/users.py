from httpx import Client
from rich.progress import Progress

from core.settings import get_settings
from models.user import MFA, User


def list_users(client: Client, filters: list[str] | None = None) -> list[User]:
    settings = get_settings()
    endpoint = "/systemusers"
    params = {"skip": 0, "limit": settings.limit, "sort": "_id"}
    for i, f in enumerate(filters or []):
        params[f"filter[{i}]"] = f
    users: list[User] = []
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
            users.extend([User(**result) for result in body.get("results")])
            params["skip"] += settings.limit
            progress.update(task, completed=params["skip"])
    return users


def get_user(client: Client, user_id: str) -> User:
    endpoint = f"/systemusers/{user_id}"
    response = client.get(endpoint)
    response.raise_for_status()
    return User(**response.json())


def update_user(client: Client, user: User) -> User:
    endpoint = f"/systemusers/{user.id}"
    data = user.model_dump(mode="json")
    response = client.put(endpoint, data=data)
    response.raise_for_status()
    return User(**response.json())


def expire_password(client: Client, user_id: str) -> None:
    endpoint = f"/systemusers/{user_id}/expire"
    response = client.post(endpoint)
    response.raise_for_status()


def update_mfa_properties(
    client: Client, user_id: str, enabled: bool, mfa: MFA
) -> None:
    endpoint = f"/systemusers/{user_id}/mfa/enforce"
    data = {
        "enable_user_portal_multifactor": enabled,
        "mfa": mfa,
    }
    response = client.post(endpoint, data=data)
    response.raise_for_status()


def sync_mfa_enrollment_status(client: Client, user_id: str) -> None:
    endpoint = f"/systemusers/{user_id}/mfasync"
    response = client.post(endpoint)
    response.raise_for_status()


def force_set_password(client: Client, user_id: str, password: str) -> None:
    endpoint = f"/systemusers/{user_id}/password"
    data = {
        "password": password,
    }
    response = client.post(endpoint, data=data)
    response.raise_for_status()


def reactivate_user(client: Client, user_id: str) -> None:
    endpoint = f"/systemusers/{user_id}/reactivate"
    response = client.post(endpoint)
    response.raise_for_status()


def reset_mfa_token(client: Client, user_id: str, mfa: MFA) -> None:
    endpoint = f"/systemusers/{user_id}/resetmfa"
    data = mfa.model_dump(mode="json", exclude={"configured"})
    response = client.post(endpoint, data=data)
    response.raise_for_status()


def activate_user(client: Client, user_id: str) -> None:
    endpoint = f"/systemusers/{user_id}/activate"
    response = client.post(endpoint)
    response.raise_for_status()


def suspend_user(client: Client, user_id: str) -> None:
    endpoint = f"/systemusers/{user_id}/state/suspend"
    response = client.post(endpoint)
    response.raise_for_status()


def unlock_user(client: Client, user_id: str) -> None:
    endpoint = f"/systemusers/{user_id}/unlock"
    response = client.post(endpoint)
    response.raise_for_status()


def find_user(client: Client, email: str) -> list[User]:
    endpoint = "/search/systemusers"
    data = {
        "searchFilter": {
            "searchTerm": email,
            "fields": ["email"],
        },
    }
    response = client.post(endpoint, json=data)
    response.raise_for_status()
    body = response.json()
    return [User(**result) for result in body.get("results")]
