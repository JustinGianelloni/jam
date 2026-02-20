#!/bin/zsh
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR" || exit 1

config_path="${JAM_CONFIG_PATH:-$HOME/.config/jam}"
config_file="$config_path/config.json"
export JAM_CONFIG_PATH="$config_path"

# Get current version from pyproject.toml
get_local_version() {
  grep -m1 '^version = ' "$SCRIPT_DIR/pyproject.toml" | sed 's/version = "\(.*\)"/\1/'
}

# Get latest release version from GitHub API
get_remote_version() {
  curl -fsSL "https://api.github.com/repos/JustinGianelloni/jam/releases/latest" 2>/dev/null | \
    jq -r '.tag_name // empty' | sed 's/^v//'
}

# Compare semantic versions: returns 0 if $1 < $2
version_lt() {
  [ "$1" = "$2" ] && return 1
  local IFS=.
  local i v1=($1) v2=($2)
  for ((i=0; i<${#v1[@]} || i<${#v2[@]}; i++)); do
    local n1=${v1[i]:-0}
    local n2=${v2[i]:-0}
    ((n1 < n2)) && return 0
    ((n1 > n2)) && return 1
  done
  return 1
}

# Check for updates (non-blocking, cached for 24 hours)
check_for_update() {
  local cache_file="$config_path/.update_check"
  local cache_ttl=86400  # 24 hours in seconds
  local now=$(date +%s)

  # Skip if recently checked
  if [[ -f "$cache_file" ]]; then
    local last_check=$(cat "$cache_file" 2>/dev/null | head -1)
    if (( now - last_check < cache_ttl )); then
      # Show cached update notice if available
      local cached_version=$(sed -n '2p' "$cache_file" 2>/dev/null)
      if [[ -n "$cached_version" ]]; then
        echo "📦 Update available: v$cached_version (current: v$(get_local_version))"
        echo "   Run 'jam update' to install the latest version."
        echo ""
      fi
      return
    fi
  fi

  # Perform check in background to avoid slowing down CLI
  (
    local remote_version=$(get_remote_version)
    local local_version=$(get_local_version)

    mkdir -p "$config_path"
    if [[ -n "$remote_version" ]] && version_lt "$local_version" "$remote_version"; then
      echo -e "$now\n$remote_version" > "$cache_file"
    else
      echo "$now" > "$cache_file"
    fi
  ) &>/dev/null &
}

# Perform update
do_update() {
  echo "Checking for updates..."
  local remote_version=$(get_remote_version)
  local local_version=$(get_local_version)

  if [[ -z "$remote_version" ]]; then
    echo "Error: Could not fetch latest version from GitHub."
    exit 1
  fi

  if version_lt "$local_version" "$remote_version"; then
    echo "Updating JAM: v$local_version → v$remote_version"
    git fetch origin --quiet
    git pull --quiet origin main

    # Clear update cache
    rm -f "$config_path/.update_check"

    echo "✅ Update complete! Now running v$remote_version"
  else
    echo "Already up to date (v$local_version)"
  fi
  exit 0
}

# Handle 'update' command
if [[ "${1:-}" == "update" ]]; then
  do_update
fi

# Check for updates (non-blocking)
check_for_update

# Check if 1password credentials need to be retrieved
if jq -e '.jam.auth.client_id_uri' "$config_file" > /dev/null 2>&1; then
  export JAM_CLIENT_ID=$(op read "$(jq -r '.jam.auth.client_id_uri' "$config_file")")
  export JAM_CLIENT_SECRET=$(op read "$(jq -r '.jam.auth.client_secret_uri' "$config_file")")
fi

uv run main.py "$@"
