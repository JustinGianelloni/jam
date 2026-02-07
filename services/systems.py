from httpx import Client
from models.system import System
from core.settings import Settings
from rich.progress import Progress

SETTINGS = Settings()


def list_all_systems(client: Client, filters: list[str] | None) -> list[System]:
    endpoint = "/systems"
    params = {
        "skip": 0,
        "limit": SETTINGS.limit,
        "sort": "_id",
    }
    print(filters)
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
            systems.extend([System(**result) for result in body.get("results")])
            params["skip"] += SETTINGS.limit
            progress.update(task, completed=params["skip"])
    return systems