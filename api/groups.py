import asyncio
from http import HTTPStatus

from core.client import get_client
from core.progress import add_task, update_task
from core.settings import get_settings
from models.group import Group

SETTINGS = get_settings()


class NoGroupsFoundError(ValueError):
    def __init__(self, filters: list[str]) -> None:
        self.filters = filters
        super().__init__()


class GroupNotFoundError(ValueError):
    def __init__(self, group_id: str) -> None:
        self.group_id = group_id
        super().__init__()


class NoGroupMembersFoundError(ValueError):
    def __init__(self, group_id: str) -> None:
        self.group_id = group_id
        super().__init__()


async def list_groups(filters: list[str]) -> list[Group]:
    endpoint = "/v2/usergroups"
    base_params: list[tuple[str, str | int | float | None]] = [
        ("limit", SETTINGS.limit)
    ]
    [base_params.append(("filter", f)) for f in filters]
    first_params = [*base_params, ("skip", 0)]
    response = await get_client().get(endpoint, params=first_params)
    response.raise_for_status()
    body = response.json()
    if not body:
        raise NoGroupsFoundError(filters)
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


async def get_group(group_id: str) -> Group:
    endpoint = f"/v2/usergroups/{group_id}"
    response = await get_client().get(endpoint)
    if response.status_code == HTTPStatus.BAD_REQUEST:
        raise GroupNotFoundError(group_id)
    response.raise_for_status()
    return Group(**response.json())


async def get_groups(group_ids: list[str]) -> list[Group]:
    task_id = add_task(
        f"Fetching {len(group_ids)} systems from JumpCloud",
        total=len(group_ids),
    )
    tasks = [get_group(group_id) for group_id in group_ids]
    groups: list[Group] = []
    for task in asyncio.as_completed(tasks):
        group = await task
        groups.append(group)
        update_task(task_id, advance=1)
    return groups


async def get_group_members(group_id: str) -> list[str]:
    endpoint = f"/v2/usergroups/{group_id}/members"
    base_params = {"limit": SETTINGS.limit}
    first_params = {**base_params, "skip": 0}
    response = await get_client().get(endpoint, params=first_params)
    if response.status_code == HTTPStatus.BAD_REQUEST:
        raise GroupNotFoundError(group_id)
    response.raise_for_status()
    body = response.json()
    if not body:
        raise NoGroupMembersFoundError(group_id)
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


async def get_groups_members(group_ids: list[str]) -> list[str]:
    task_id = add_task(
        f"Fetching {len(group_ids)} groups from JumpCloud",
        total=len(group_ids),
    )
    tasks = [get_group_members(group_id) for group_id in group_ids]
    members: list[str] = []
    for task in asyncio.as_completed(tasks):
        group = await task
        members.extend(group)
        update_task(task_id, advance=1)
    return members


async def add_group_member(group_id: str, user_id: str) -> None:
    endpoint = f"/v2/usergroups/{group_id}/members"
    data = {
        "op": "add",
        "type": "user",
        "id": user_id,
    }
    response = await get_client().post(endpoint, json=data)
    response.raise_for_status()


async def remove_group_member(group_id: str, user_id: str) -> None:
    endpoint = f"/v2/usergroups/{group_id}/members"
    data = {
        "op": "remove",
        "type": "user",
        "id": user_id,
    }
    response = await get_client().post(endpoint, json=data)
    response.raise_for_status()
