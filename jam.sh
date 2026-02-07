#!/bin/zsh
cd "$(dirname "$0")"

# Fetch and pull changes
git fetch origin --quiet main > /dev/null
LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse @{u})

if [ "$LOCAL" != "$REMOTE" ]; then
    git pull > /dev/null
fi

uv run main.py "$@"