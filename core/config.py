import json
import os
from pathlib import Path
from typing import Any

import httpx
import tomlkit

PROJECT_ROOT = Path(__file__).parent.parent
PYPROJECT_PATH = PROJECT_ROOT / "pyproject.toml"


def get_repo_url() -> str:
    with PYPROJECT_PATH.open() as file:
        pyproject = tomlkit.load(file)
    return str(pyproject["project"]["urls"]["Repository"])


def get_default_config_url() -> str:
    repo_url = get_repo_url()
    # Convert https://github.com/user/repo to https://raw.githubusercontent.com/user/repo/main
    raw_url = repo_url.replace("github.com", "raw.githubusercontent.com")
    return f"{raw_url}/main/default_config.json"


def get_config_dir() -> Path:
    path = os.getenv("JAM_CONFIG_PATH")
    if not path:
        err = "Missing JAM_CONFIG_PATH in environment."
        raise RuntimeError(err)
    config_dir = Path(path)
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def get_config_path() -> Path:
    return get_config_dir() / "config.json"


def get_default_config() -> dict[str, Any]:
    url = get_default_config_url()
    response = httpx.get(url, timeout=10)
    response.raise_for_status()
    return response.json()


def init_config() -> Path:
    config_path = get_config_path()
    if not config_path.exists():
        default_config = get_default_config()
        with Path.open(config_path, "w") as file:
            json.dump(default_config, file, indent=2)
    return config_path


def load_config() -> dict[str, Any]:
    config_path = init_config()
    with Path.open(config_path) as file:
        return json.load(file)
