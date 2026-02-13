#!/bin/bash
use_op=0
tools=("jq" "yq" "uv" "fzf")

# Confirm intent and dependencies
echo "This script assumes you have Homebrew, Git, and 1Password CLI (if selected) installed."
read -r -e -p "Do you wish to continue? (y/N): " confirm
if [[ "$confirm" != [yY] && "$confirm" != [yY][eE][sS] ]]; then
  echo "Installation aborted."
  exit 1
else
  read -r -e -p "Do you wish to retrieve credentials from 1Password? (y/N): " op_confirm
  if [[ "$op_confirm" == [yY] || "$op_confirm" == [yY][eE][sS] ]]; then
    use_op=1
  fi
fi

# Install missing dependencies with one brew command
missing=()
for tool in "${tools[@]}"; do
  command -v "$tool" &>/dev/null || missing+=("$tool")
done
if (( ${#missing[@]} )); then
  echo "Installing: ${missing[*]}"
  brew install "${missing[@]}"
else
  echo "All dependencies already installed."
fi

choose_field() {
  local prompt_text=$1
  echo "$op_json" | \
  jq -r '.fields[] | "\(.label): \(.reference)"' | \
  fzf --prompt="$prompt_text" --height=10% --reverse | sed 's/.*: //'
}

# Retrieve credentials from 1Password if selected
get_op_creds () {
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
  if grep -q '^client_id_uri = ' pyproject.toml; then
    sed -i '' 's|^client_id_uri = .*|client_id_uri = "'"$client_id"'"|' pyproject.toml
  else
    sed -i '' '/^\[tool\.auth\]/a\'$'\n''client_id_uri = "'"$client_id"'"' pyproject.toml
  fi
  if grep -q '^client_secret_uri = ' pyproject.toml; then
    sed -i '' 's|^client_secret_uri = .*|client_secret_uri = "'"$client_secret"'"|' pyproject.toml
  else
    sed -i '' '/^\[tool\.auth\]/a\'$'\n''client_secret_uri = "'"$client_secret"'"' pyproject.toml
  fi
}

if (( use_op )); then
  get_op_creds
fi

# Add local config files to .gitignore to prevent syncing upstream
echo "Adding local config files to .gitignore..."
{
  echo "*.toml"
  echo ".gitignore"
} >> .gitignore

# Check if alias already exists, add if it doesn't
if grep -qF "alias jam=" ~/.zshrc; then
  echo "Alias for jam already exists. If issues persist, check your .zshrc file."
else
  echo "Adding alias for jam to .zshrc..."
  script_dir="$(cd "$(dirname "$0")" && pwd)"
  echo "alias jam=\"${script_dir}/jam.sh\"" >> ~/.zshrc
  echo "Run 'source ~/.zshrc' or restart your terminal to start using the 'jam' command."
fi