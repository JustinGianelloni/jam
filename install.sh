#!/bin/bash
set -euo pipefail

# Configuration
REPO="JustinGianelloni/jam"
INSTALL_DIR="${JAM_INSTALL_DIR:-$HOME/.local/share/jam}"
CONFIG_PATH="${JAM_CONFIG_PATH:-$HOME/.config/jam}"
CONFIG_FILE="$CONFIG_PATH/config.json"
CONFIG_URL="https://raw.githubusercontent.com/${REPO}/main/default_config.json"

use_op=0
shell_rc="${ZDOTDIR:-$HOME}/.zshrc"
[[ "$SHELL" == */bash ]] && shell_rc="$HOME/.bashrc"
tools=("jq" "uv" "fzf" "curl" "tar")

get_latest_version() {
  curl -fsSL "https://api.github.com/repos/${REPO}/releases/latest" | jq -r '.tag_name'
}

get_current_version() {
  local pyproject_file="$INSTALL_DIR/pyproject.toml"
  if [[ -f "$pyproject_file" ]]; then
    grep -oP '^version = "\K[^"]+' "$pyproject_file" | head -1
  else
    echo ""
  fi
}

download_release() {
  local version=$1
  local tarball_url="https://github.com/${REPO}/archive/refs/tags/${version}.tar.gz"
  local temp_dir
  temp_dir=$(mktemp -d)

  echo "Downloading JAM ${version}..."
  curl -fsSL "$tarball_url" -o "$temp_dir/jam.tar.gz"

  echo "Extracting..."
  tar -xzf "$temp_dir/jam.tar.gz" -C "$temp_dir"

  # Remove old installation (preserve nothing from install dir)
  rm -rf "$INSTALL_DIR"
  mkdir -p "$INSTALL_DIR"

  # Move extracted contents (archive extracts to jam-<version> folder)
  mv "$temp_dir"/jam-*/* "$INSTALL_DIR/"


  # Cleanup
  rm -rf "$temp_dir"
}

install_pkg() {
  local pkg=$1
  if command -v brew &>/dev/null; then
    brew install "$pkg"
  elif command -v apt-get &>/dev/null; then
    sudo apt-get install -y "$pkg"
  elif command -v dnf &>/dev/null; then
    sudo dnf install -y "$pkg"
  elif command -v pacman &>/dev/null; then
    sudo pacman -S --noconfirm "$pkg"
  elif command -v apk &>/dev/null; then
    sudo apk add "$pkg"
  else
    echo "Error: No supported package manager found. Install '$pkg' manually."
    return 1
  fi
}

install_uv() {
  if ! command -v uv &>/dev/null; then
    echo "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
  fi
}

choose_field() {
  local prompt_text=$1
  echo "$op_json" | \
  jq -r '.fields[] | "\(.label): \(.reference)"' | \
  fzf --prompt="$prompt_text" --height=10% --reverse | sed 's/.*: //'
}

get_op_creds() {
  read -r -e -p "What is the name of the saved credential in 1Password (e.g. JC_OAUTH)? " op_title
  op_json=$(op item get "$op_title" --format json)
  if [[ -z "$op_json" ]]; then
    echo "No credential found by that name. Please validate your credential name and run the script again."
    exit 1
  fi
  echo "--- Select the Client ID ---"
  client_id=$(choose_field "Select Client ID: ")
  echo "--- Select the Client Secret ---"
  client_secret=$(choose_field "Select Client Secret: ")
  if [[ -n "$client_id" && -n "$client_secret" ]]; then
    echo -e "\nReferences captured:"
    echo "Client ID:      $client_id"
    echo "Client Secret:  $client_secret"
  fi
  jq --arg id "$client_id" --arg secret "$client_secret" \
    '.jam.auth.client_id_uri = $id | .jam.auth.client_secret_uri = $secret' \
    "$CONFIG_FILE" > "$CONFIG_FILE.tmp" && mv "$CONFIG_FILE.tmp" "$CONFIG_FILE"
}

# --- Main Installation ---

echo "=== JAM Installer ==="
echo "This will install JAM and its dependencies."
echo "  Install directory: $INSTALL_DIR"
echo "  Config directory:  $CONFIG_PATH"
echo ""

read -r -e -p "Do you wish to continue? (y/N): " confirm
if [[ "$confirm" != [yY] && "$confirm" != [yY][eE][sS] ]]; then
  echo "Installation aborted."
  exit 1
fi

read -r -e -p "Do you wish to retrieve credentials from 1Password? (y/N): " op_confirm
if [[ "$op_confirm" == [yY] || "$op_confirm" == [yY][eE][sS] ]]; then
  use_op=1
  tools+=("op")
fi

# Install missing dependencies (except uv which has its own installer)
echo "Checking dependencies..."
missing=()
for tool in "${tools[@]}"; do
  [[ "$tool" == "uv" ]] && continue
  command -v "$tool" &>/dev/null || missing+=("$tool")
done

if (( ${#missing[@]} )); then
  echo "Installing missing tools: ${missing[*]}"
  for pkg in "${missing[@]}"; do
    install_pkg "$pkg"
  done
fi

# Install uv using official installer
install_uv

# Get latest version and check if update needed
latest_version=$(get_latest_version)
current_version=$(get_current_version)

if [[ -z "$latest_version" ]]; then
  echo "Error: Could not fetch latest release. Check your internet connection."
  exit 1
fi

# Strip 'v' prefix from latest_version for comparison with pyproject.toml version
latest_version_num="${latest_version#v}"

if [[ "$current_version" == "$latest_version_num" ]]; then
  echo "JAM ${latest_version} is already installed."
else
  if [[ -n "$current_version" ]]; then
    echo "Updating from v${current_version} to ${latest_version}..."
  fi
  download_release "$latest_version"
fi

# Create config directory and download default config
mkdir -p "$CONFIG_PATH"
if [[ ! -f "$CONFIG_FILE" ]]; then
  echo "Downloading default configuration..."
  curl -fsSL "$CONFIG_URL" -o "$CONFIG_FILE"
else
  echo "Config file already exists, skipping download."
fi

# Configure 1Password credentials if selected
if (( use_op )); then
  get_op_creds
fi

# Add shell alias
if grep -qF "alias jam=" "$shell_rc"; then
  echo "Alias for jam already exists."
else
  echo "Adding alias for jam to $shell_rc..."
  echo "alias jam=\"$INSTALL_DIR/jam.sh\"" >> "$shell_rc"
fi

# Export config path in shell rc if not already present
if ! grep -qF "JAM_CONFIG_PATH" "$shell_rc"; then
  echo "export JAM_CONFIG_PATH=\"$CONFIG_PATH\"" >> "$shell_rc"
fi

echo ""
echo "=== Installation Complete ==="
echo "Installed JAM ${latest_version}"
echo "Run 'source $shell_rc' or restart your terminal to start using the 'jam' command."
