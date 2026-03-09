import asyncio
from http import HTTPStatus

from core.client import get_client
from core.progress import add_task, update_task
from core.settings import get_settings
from models.system import Association, System

SETTINGS = get_settings()


class SystemNotFoundError(ValueError):
    def __init__(self, system_id: str) -> None:
        self.system_id = system_id
        super().__init__()


class NoSystemsFoundError(ValueError):
    def __init__(self, filters: list[str]) -> None:
        self.filters = filters
        super().__init__()


class SystemSearchEmptyError(ValueError):
    def __init__(self, field: str, value: str) -> None:
        self.field = field
        self.value = value
        super().__init__()


class NoAssociationsFoundError(ValueError):
    def __init__(self, system_id: str) -> None:
        self.system_id = system_id
        super().__init__()


async def list_systems(filters: list[str]) -> list[System]:
    endpoint = "/systems"
    base_params = {
        "limit": SETTINGS.limit,
        "sort": "_id",
    }
    for i, f in enumerate(filters or []):
        base_params[f"filter[{i}]"] = f
    first_params = {**base_params, "skip": 0}
    response = await get_client().get(endpoint, params=first_params)
    response.raise_for_status()
    body = response.json()
    if not body.get("results"):
        raise NoSystemsFoundError(filters)
    total = body.get("totalCount", 0)
    systems = [System(**result) for result in body.get("results")]
    if len(systems) == total:
        return systems
    task_id = add_task(
        "Fetching systems from JumpCloud",
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
            results = response.json().get("results")
            systems.extend([System(**result) for result in results])
            update_task(task_id, advance=len(systems))
    return systems


async def get_system(system_id: str) -> System:
    endpoint = f"/systems/{system_id}"
    response = await get_client().get(endpoint)
    if response.status_code == HTTPStatus.BAD_REQUEST:
        raise SystemNotFoundError(system_id)
    response.raise_for_status()
    return System(**response.json())


async def get_systems(system_ids: list[str]) -> list[System]:
    task_id = add_task(
        f"Fetching {len(system_ids)} systems from JumpCloud",
        total=len(system_ids),
    )
    tasks = [get_system(system_id) for system_id in system_ids]
    systems: list[System] = []
    for task in asyncio.as_completed(tasks):
        system = await task
        systems.append(system)
        update_task(task_id, advance=len(system_ids))
    return systems


async def get_fde_key(system_id: str) -> str:
    endpoint = f"/v2/systems/{system_id}/fdekey"
    response = await get_client().get(endpoint)
    if response.status_code == HTTPStatus.BAD_REQUEST:
        raise SystemNotFoundError(system_id)
    response.raise_for_status()
    return response.json().get("key")


async def find_system(field: str, value: str) -> list[System]:
    endpoint = "/search/systems"
    data = {
        "searchFilter": {
            "searchTerm": value,
            "fields": [field],
        },
    }
    response = await get_client().post(endpoint, json=data)
    response.raise_for_status()
    body = response.json()
    if not body.get("results"):
        raise SystemSearchEmptyError(field, value)
    return [System(**result) for result in body.get("results")]


async def list_associations(target: str, system_id: str) -> list[Association]:
    endpoint = f"/v2/systems/{system_id}/associations"
    params = {"targets": target}
    response = await get_client().get(endpoint, params=params)
    response.raise_for_status()
    body = response.json()
    if not body:
        raise NoAssociationsFoundError(system_id)
    return [Association(**association) for association in body]
