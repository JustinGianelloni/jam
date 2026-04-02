#!/bin/bash
set -euo pipefail

REPO="JustinGianelloni/jam"
INSTALL_DIR="${JAM_INSTALL_DIR:-$HOME/.local/bin}"
CONFIG_DIR="$HOME/.config/jam"
CONFIG_FILE="$CONFIG_DIR/config.json"

use_op=0
tools=("jq" "fzf" "curl")

get_latest_version() {
  curl -fsSL "https://api.github.com/repos/${REPO}/releases/latest" | jq -r '.tag_name'
}

detect_platform() {
  local os arch
  os=$(uname -s | tr '[:upper:]' '[:lower:]')
  arch=$(uname -m)
  case "$arch" in
    x86_64)  arch="amd64" ;;
    aarch64|arm64) arch="arm64" ;;
    *) echo "Error: Unsupported architecture: $arch" >&2; exit 1 ;;
  esac
  echo "${os}_${arch}"
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

choose_field() {
  local prompt_text=$1
  echo "$op_json" | \
    jq -r '.fields[] | "\(.label): \(.reference)"' | \
    fzf --prompt="$prompt_text" --height=10% --reverse | sed 's/.*: //'
}

get_op_account() {
  local accounts
  accounts=$(op account list --format json 2>/dev/null || echo "[]")
  local count
  count=$(echo "$accounts" | jq 'length')

  if [[ "$count" -eq 0 ]]; then
    echo "No 1Password accounts found. Please sign in to 1Password first."
    exit 1
  elif [[ "$count" -eq 1 ]]; then
    echo "$accounts" | jq -r '.[0].account_uuid'
  else
    echo "$accounts" | \
      jq -r '.[] | "\(.email) (\(.url)): \(.account_uuid)"' | \
      fzf --prompt="Select 1Password account: " --height=10% --reverse | sed 's/.*: //'
  fi
}

get_op_creds() {
  echo ""
  echo "--- 1Password Credential Setup ---"
  echo ""

  op_account=$(get_op_account)
  if [[ -z "$op_account" ]]; then
    echo "No account selected. Skipping 1Password setup."
    return
  fi
  echo "Using 1Password account: $op_account"

  read -r -e -p "What is the name of the saved credential in 1Password (e.g. JC_OAUTH)? " op_title </dev/tty
  op_json=$(op item get "$op_title" --format json)
  if [[ -z "$op_json" ]]; then
    echo "No credential found by that name. Please validate your credential name and run the script again."
    exit 1
  fi

  echo "--- Select the Client ID ---"
  client_id_uri=$(choose_field "Select Client ID: ")
  echo "--- Select the Client Secret ---"
  client_secret_uri=$(choose_field "Select Client Secret: ")

  if [[ -n "$client_id_uri" && -n "$client_secret_uri" ]]; then
    echo ""
    echo "References captured:"
    echo "  Account:        $op_account"
    echo "  Client ID:      $client_id_uri"
    echo "  Client Secret:  $client_secret_uri"
  fi

  jq --arg account "$op_account" \
     --arg id "$client_id_uri" \
     --arg secret "$client_secret_uri" \
     '.OP_ACCOUNT = $account | .OP_CLIENT_ID_URI = $id | .OP_CLIENT_SECRET_URI = $secret' \
     "$CONFIG_FILE" > "$CONFIG_FILE.tmp" && mv "$CONFIG_FILE.tmp" "$CONFIG_FILE"
}

write_default_config() {
  cat > "$CONFIG_FILE" <<'CONF'
{
  "OP_ACCOUNT": "",
  "OP_CLIENT_ID_URI": "",
  "OP_CLIENT_SECRET_URI": ""
}
CONF
}

# --- Main Installation ---

echo "=== JAM Installer ==="
echo "This will install JAM and its dependencies."
echo "  Binary location: $INSTALL_DIR/jam"
echo "  Config file:     $CONFIG_FILE"
echo ""

read -r -e -p "Do you wish to continue? (y/N): " confirm </dev/tty
if [[ "$confirm" != [yY] && "$confirm" != [yY][eE][sS] ]]; then
  echo "Installation aborted."
  exit 1
fi

read -r -e -p "Do you wish to retrieve credentials from 1Password? (y/N): " op_confirm </dev/tty
if [[ "$op_confirm" == [yY] || "$op_confirm" == [yY][eE][sS] ]]; then
  use_op=1
  tools+=("op")
fi

# Install missing dependencies
echo ""
echo "Checking dependencies..."
missing=()
for tool in "${tools[@]}"; do
  command -v "$tool" &>/dev/null || missing+=("$tool")
done

if (( ${#missing[@]} )); then
  echo "Installing missing tools: ${missing[*]}"
  for pkg in "${missing[@]}"; do
    install_pkg "$pkg"
  done
fi

# Get latest version
latest_version=$(get_latest_version)
if [[ -z "$latest_version" ]]; then
  echo "Error: Could not fetch latest release. Check your internet connection."
  exit 1
fi

# Detect platform and download binary
platform=$(detect_platform)
ext=""
if [[ "$platform" == windows_* ]]; then ext=".exe"; fi
binary_url="https://github.com/${REPO}/releases/download/${latest_version}/jam_${platform}${ext}"

echo ""
echo "Downloading jam ${latest_version} for ${platform}..."
mkdir -p "$INSTALL_DIR"
curl -fsSL "$binary_url" -o "$INSTALL_DIR/jam${ext}"
chmod +x "$INSTALL_DIR/jam${ext}"

# Create config directory and write default config
mkdir -p "$CONFIG_DIR"
echo "Writing config to $CONFIG_FILE..."
write_default_config

# Configure 1Password credentials if selected
if (( use_op )); then
  get_op_creds
fi

# Ensure ~/.local/bin is in PATH
shell_rc="${ZDOTDIR:-$HOME}/.zshrc"
[[ "$SHELL" == */bash ]] && shell_rc="$HOME/.bashrc"

if ! echo "$PATH" | tr ':' '\n' | grep -qx "$INSTALL_DIR"; then
  if ! grep -qF "$INSTALL_DIR" "$shell_rc" 2>/dev/null; then
    echo "Adding $INSTALL_DIR to PATH in $shell_rc..."
    echo "export PATH=\"$INSTALL_DIR:\$PATH\"" >> "$shell_rc"
  fi
fi

echo ""
echo "=== Installation Complete ==="
echo "Installed jam ${latest_version} to $INSTALL_DIR/jam${ext}"
echo "Config written to $CONFIG_FILE"
if ! echo "$PATH" | tr ':' '\n' | grep -qx "$INSTALL_DIR"; then
  echo "Run 'source $shell_rc' or restart your terminal to start using jam."
else
  echo "Run 'jam --help' to get started."
fi
