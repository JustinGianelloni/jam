#!/bin/zsh
cd "$(dirname "$0")"

# Fetch and pull changes
git fetch origin --quiet main > /dev/null
LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse @{u})

if [ "$LOCAL" != "$REMOTE" ]; then
    git pull > /dev/null
fi

#Check if 1password credentials need to be retrieved
if grep -q '^client_id_uri = ' pyproject.toml; then
  export JAM_CLIENT_ID=$(op read "$(yq '.tool.auth.client_id_uri' pyproject.toml)")
  export JAM_CLIENT_SECRET=$(op read "$(yq '.tool.auth.client_secret_uri' pyproject.toml)")
fi

uv run main.py "$@"
