from httpx import Client
from rich.progress import Progress

from core.settings import get_settings
from models.system import Association, System


def list_systems(
    client: Client, filters: list[str] | None = None
) -> list[System]:
    settings = get_settings()
    endpoint = "/systems"
    params = {
        "skip": 0,
        "limit": settings.limit,
        "sort": "_id",
    }
    for i, f in enumerate(filters or []):
        params[f"filter[{i}]"] = f
    systems: list[System] = []
    total: int | None = None
    with Progress() as progress:
        task = progress.add_task("Fetching systems from JumpCloud", total=None)
        while total is None or params["skip"] < total:
            response = client.get(endpoint, params=params)
            response.raise_for_status()
            body = response.json()
            if total is None:
                total = body.get("totalCount", 0)
                progress.update(task, total=total)
            systems.extend(
                [System(**result) for result in body.get("results")]
            )
            params["skip"] += settings.limit
            progress.update(task, completed=params["skip"])
    return systems


def get_system(client: Client, system_id: str) -> System:
    endpoint = f"/systems/{system_id}"
    response = client.get(endpoint)
    response.raise_for_status()
    return System(**response.json())


def get_fde_key(client: Client, system_id: str) -> str:
    endpoint = f"/v2/systems/{system_id}/fdekey"
    response = client.get(endpoint)
    response.raise_for_status()
    return response.json().get("key")


def find_system(client: Client, query: str) -> list[System]:
    endpoint = "/search/systems"
    data = {
        "searchFilter": {
            "searchTerm": query,
            "fields": ["hostname", "serialNumber"],
        },
    }
    response = client.post(endpoint, json=data)
    response.raise_for_status()
    body = response.json()
    return [System(**result) for result in body.get("results")]


def list_associations(
    client: Client, target: str, system_id: str
) -> list[Association]:
    endpoint = f"/v2/systems/{system_id}/associations"
    params = {"targets": target}
    response = client.get(endpoint, params=params)
    response.raise_for_status()
    body = response.json()
    return [Association(**association) for association in body]
