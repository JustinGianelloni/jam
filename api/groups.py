import asyncio

from core.client import get_client
from core.progress import add_task, update_task
from core.settings import get_settings
from models.group import Group

SETTINGS = get_settings()


async def list_groups(filters: list[str]) -> list[Group]:
    endpoint = "/v2/usergroups"
    base_params: list[tuple[str, str | int]] = [("limit", SETTINGS.limit)]
    [base_params.append(("filter", f)) for f in filters]
    first_params = [*base_params, ("skip", 0)]
    response = await get_client().get(endpoint, params=first_params)
    response.raise_for_status()
    body = response.json()
    total = int(response.headers.get("x-total-count"))
    groups = [Group(**result) for result in body]
    if len(groups) == total:
        return groups
    task_id = add_task(
        "Fetching user groups from JumpCloud",
        total=total,
        completed=SETTINGS.limit,
    )
    async with get_client() as client:
        tasks = []
        skip = SETTINGS.limit
        while skip < total:
            page_params = [*base_params, ("skip", skip)]
            tasks.append(client.get(endpoint, params=page_params))
            skip += SETTINGS.limit
        for task in asyncio.as_completed(tasks):
            response = await task
            response.raise_for_status()
            body = response.json()
            groups.extend(Group(**result) for result in body)
            update_task(task_id, advance=len(body))
    return groups


async def get_group_members(group_id: str) -> list[str]:
    endpoint = f"/v2/usergroups/{group_id}/members"
    base_params = {"limit": SETTINGS.limit}
    first_params = {**base_params, "skip": 0}
    response = await get_client().get(endpoint, params=first_params)
    response.raise_for_status()
    body = response.json()
    total = int(response.headers.get("x-total-count"))
    users = [result["to"]["id"] for result in body]
    if len(users) == total:
        return users
    task_id = add_task(
        "Fetching group members from JumpCloud",
        total=total,
        completed=SETTINGS.limit,
    )
    async with get_client() as client:
        tasks = []
        skip = SETTINGS.limit
        while skip < total:
            page_params = {**base_params, "skip": skip}
            tasks.append(client.get(endpoint, params=page_params))
            skip += SETTINGS.limit
        for task in asyncio.as_completed(tasks):
            response = await task
            response.raise_for_status()
            body = response.json()
            users.extend(result["to"]["id"] for result in body)
            update_task(task_id, advance=len(body))
    return users
