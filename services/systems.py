from httpx import Client
from rich.progress import Progress

from core.settings import Settings
from models.system import System

SETTINGS = Settings()


def list_all_systems(
    client: Client, filters: list[str] | None
) -> list[System]:
    endpoint = "/systems"
    params = {
        "skip": 0,
        "limit": SETTINGS.limit,
        "sort": "_id",
    }
    if filters:
        for i, f in enumerate(filters):
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
            params["skip"] += SETTINGS.limit
            progress.update(task, completed=params["skip"])
    return systems


def list_system(client: Client, system_id_: str) -> System:
    endpoint = f"/systems/{system_id_}"
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


def list_bound_systems(client: Client, user_id: str) -> list[str]:
    endpoint = f"/v2/users/{user_id}/systems"
    response = client.get(endpoint)
    response.raise_for_status()
    body = response.json()
    return [result.get("id") for result in body]
