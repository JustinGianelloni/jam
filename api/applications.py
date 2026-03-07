import asyncio

from core.client import get_client
from core.progress import add_task, update_task
from core.settings import get_settings
from models.application import Application

SETTINGS = get_settings()


async def list_applications(
    filters: list[str] | None = None,
) -> list[Application]:
    endpoint = "/applications"
    base_params = {"limit": SETTINGS.limit, "sort": "_id"}
    for i, f in enumerate(filters or []):
        base_params[f"filter[{i}]"] = f
    first_params = {**base_params, "skip": 0}
    response = await get_client().get(endpoint, params=first_params)
    response.raise_for_status()
    body = response.json()
    total = body.get("totalCount", 0)
    apps = [Application(**result) for result in body.get("results")]
    if len(apps) == total:
        return apps
    task_id = add_task(
        "Fetching applications from JumpCloud",
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
            apps.extend(Application(**result) for result in results)
            update_task(task_id, advance=len(results))
    return apps


async def list_associations(app_id: str) -> list[str]:
    endpoint = f"/v2/applications/{app_id}/associations"
    base_params: list[tuple[str, str | int | float | None]] = [
        ("limit", SETTINGS.limit),
        ("targets", "user_group"),
    ]
    first_params = [*base_params, ("skip", 0)]
    response = await get_client().get(endpoint, params=first_params)
    response.raise_for_status()
    total = int(response.headers.get("x-total-count"))
    groups = [str(result.get("to").get("id")) for result in response.json()]
    if len(groups) == total:
        return groups
    task_id = add_task(
        "Fetching associated user groups from JumpCloud",
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
            groups.extend(str(result.get("to").get("id")) for result in body)
            update_task(task_id, advance=len(body))
    return groups
