import asyncio

from rich.progress import Progress

from core.client import get_client
from core.settings import get_settings
from models.user import MFA, User


async def list_users(filters: list[str] | None = None) -> list[User]:
    settings = get_settings()
    endpoint = "/systemusers"
    base_params = {"limit": settings.limit, "sort": "_id"}
    for i, f in enumerate(filters or []):
        base_params[f"filter[{i}]"] = f
    first_params = {**base_params, "skip": 0}
    response = await get_client().get(endpoint, params=first_params)
    response.raise_for_status()
    body = response.json()
    total = body.get("totalCount", 0)
    users = [User(**result) for result in body.get("results")]
    if len(users) == total:
        return users
    async with get_client() as client:
        with Progress() as progress:
            work = progress.add_task(
                "Fetching users from JumpCloud",
                total=total,
                completed=settings.limit,
            )
            tasks = []
            skip = settings.limit
            while skip < total:
                page_params = {**base_params, "skip": skip}
                tasks.append(client.get(endpoint, params=page_params))
                skip += settings.limit
            for task in asyncio.as_completed(tasks):
                response = await task
                response.raise_for_status()
                results = response.json().get("results")
                users.extend(User(**result) for result in results)
                progress.update(work, advance=len(results))
    return users


async def get_user(user_id: str) -> User:
    endpoint = f"/systemusers/{user_id}"
    response = await get_client().get(endpoint)
    response.raise_for_status()
    return User(**response.json())


async def get_users(user_ids: list[str]) -> list[User]:
    with Progress() as progress:
        work = progress.add_task(
            f"Fetching {len(user_ids)} users from JumpCloud",
            total=len(user_ids),
        )
        tasks = [get_user(user_id) for user_id in user_ids]
        users: list[User] = []
        for task in asyncio.as_completed(tasks):
            user = await task
            users.append(user)
            progress.update(work, advance=1)
    return users


async def update_user(user: User) -> User:
    endpoint = f"/systemusers/{user.id}"
    data = user.model_dump(mode="json")
    response = await get_client().put(endpoint, data=data)
    response.raise_for_status()
    return User(**response.json())


async def expire_password(user_id: str) -> None:
    endpoint = f"/systemusers/{user_id}/expire"
    response = await get_client().post(endpoint)
    response.raise_for_status()


async def update_mfa_properties(user_id: str, enabled: bool, mfa: MFA) -> None:
    endpoint = f"/systemusers/{user_id}/mfa/enforce"
    data = {
        "enable_user_portal_multifactor": enabled,
        "mfa": mfa,
    }
    response = await get_client().post(endpoint, data=data)
    response.raise_for_status()


async def sync_mfa_enrollment_status(user_id: str) -> None:
    endpoint = f"/systemusers/{user_id}/mfasync"
    response = await get_client().post(endpoint)
    response.raise_for_status()


async def force_set_password(user_id: str, password: str) -> None:
    endpoint = f"/systemusers/{user_id}/password"
    data = {
        "password": password,
    }
    response = await get_client().post(endpoint, data=data)
    response.raise_for_status()


async def reactivate_user(user_id: str) -> None:
    endpoint = f"/systemusers/{user_id}/reactivate"
    response = await get_client().post(endpoint)
    response.raise_for_status()


async def reset_mfa_token(user_id: str, mfa: MFA) -> None:
    endpoint = f"/systemusers/{user_id}/resetmfa"
    data = mfa.model_dump(mode="json", exclude={"configured"})
    response = await get_client().post(endpoint, data=data)
    response.raise_for_status()


async def activate_user(user_id: str) -> None:
    endpoint = f"/systemusers/{user_id}/activate"
    response = await get_client().post(endpoint)
    response.raise_for_status()


async def suspend_user(user_id: str) -> None:
    endpoint = f"/systemusers/{user_id}/state/suspend"
    response = await get_client().post(endpoint)
    response.raise_for_status()


async def unlock_user(user_id: str) -> None:
    endpoint = f"/systemusers/{user_id}/unlock"
    response = await get_client().post(endpoint)
    response.raise_for_status()


async def find_user(email: str) -> list[User]:
    endpoint = "/search/systemusers"
    data = {
        "searchFilter": {
            "searchTerm": email,
            "fields": ["email"],
        },
    }
    response = await get_client().post(endpoint, json=data)
    response.raise_for_status()
    body = response.json()
    return [User(**result) for result in body.get("results")]


async def list_bound_systems(user_id: str) -> list[str]:
    endpoint = f"/v2/users/{user_id}/systems"
    response = await get_client().get(endpoint)
    response.raise_for_status()
    body = response.json()
    return [result.get("id") for result in body]
