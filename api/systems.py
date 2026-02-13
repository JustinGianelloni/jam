import asyncio

from rich.progress import Progress

from core.client import get_client
from core.settings import get_settings
from models.system import Association, System


async def list_systems(filters: list[str] | None = None) -> list[System]:
    settings = get_settings()
    endpoint = "/systems"
    base_params = {
        "limit": settings.limit,
        "sort": "_id",
    }
    for i, f in enumerate(filters or []):
        base_params[f"filter[{i}]"] = f
    first_params = {**base_params, "skip": 0}
    response = await get_client().get(endpoint, params=first_params)
    response.raise_for_status
    body = response.json()
    total = body.get("totalCount", 0)
    systems = [System(**result) for result in body.get("results")]
    if len(systems) == total:
        return systems
    async with get_client() as client:
        with Progress() as progress:
            work = progress.add_task(
                "Fetching systems from JumpCloud",
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
                systems.extend([System(**result) for result in results])
                progress.update(work, advance=len(results))
    return systems


async def get_system(system_id: str) -> System:
    endpoint = f"/systems/{system_id}"
    response = await get_client().get(endpoint)
    response.raise_for_status()
    return System(**response.json())


async def get_systems(system_ids: list[str]) -> list[System]:
    with Progress() as progress:
        work = progress.add_task(
            f"Fetching {len(system_ids)} systems from JumpCloud",
            total=len(system_ids),
        )
        tasks = [get_system(system_id) for system_id in system_ids]
        systems: list[System] = []
        for task in asyncio.as_completed(tasks):
            system = await task
            systems.append(system)
            progress.update(work, advance=1)
    return systems


async def get_fde_key(system_id: str) -> str:
    endpoint = f"/v2/systems/{system_id}/fdekey"
    response = await get_client().get(endpoint)
    response.raise_for_status()
    return response.json().get("key")


async def find_system(query: str) -> list[System]:
    endpoint = "/search/systems"
    data = {
        "searchFilter": {
            "searchTerm": query,
            "fields": ["hostname", "serialNumber"],
        },
    }
    response = await get_client().post(endpoint, json=data)
    response.raise_for_status()
    body = response.json()
    return [System(**result) for result in body.get("results")]


async def list_associations(target: str, system_id: str) -> list[Association]:
    endpoint = f"/v2/systems/{system_id}/associations"
    params = {"targets": target}
    response = await get_client().get(endpoint, params=params)
    response.raise_for_status()
    body = response.json()
    return [Association(**association) for association in body]
