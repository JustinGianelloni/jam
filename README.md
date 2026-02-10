# JAM - JumpCloud Admin Manager

A command-line interface for managing JumpCloud users and systems.

## Features

- List and search JumpCloud system users
- List and search JumpCloud systems
- Retrieve full disk encryption (FDE) keys
- Find systems bound to specific users
- Export data to CSV files
- Supports Unix pipes for command chaining
- Optional 1Password integration for credential management

## Prerequisites

- macOS
- [Homebrew](https://brew.sh/)
- Git
- Python 3.13+
- JumpCloud Admin OAuth credentials (Client ID and Client Secret)
- [1Password CLI](https://developer.1password.com/docs/cli/) (optional, for credential storage)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-org/jam.git
   cd jam
   ```

2. Run the installation script:
   ```bash
   ./install.sh
   ```

   The script will:
   - Install required dependencies (`jq`, `yq`, `uv`, `fzf`) via Homebrew
   - Optionally configure 1Password credential references
   - Add a `jam` alias to your `.zshrc`

3. Reload your shell or run:
   ```bash
   source ~/.zshrc
   ```

4. If not using 1Password, manually configure your credentials in a `.env` file in the project root:
   ```bash
   CLIENT_ID=your-client-id
   CLIENT_SECRET=your-client-secret
   ```

## Commands

### User Commands

#### `list-users`
List all system users in JumpCloud.

```bash
jam list-users [OPTIONS]
```

**Options:**
- `--filter` - Filter using JumpCloud's filter syntax (e.g., `employeeType:$eq:Contractor`). Can be used multiple times.
- `--department` - Filter users by department (e.g., `Engineering`)
- `--cost-center` - Filter users by cost center (e.g., `Data Engineering`)
- `--title` - Filter users by job title (e.g., `Data Engineer`)
- `--state` - Filter users by state (`ACTIVATED`, `SUSPENDED`, or `STAGED`)
- `--csv FILE` - Export results to a CSV file

**Examples:**
```bash
jam list-users
jam list-users --state ACTIVATED
jam list-users --department Engineering --state ACTIVATED
jam list-users --filter 'employeeType:$eq:Contractor'
jam list-users --csv users.csv
```

#### `get-user`
Get a JumpCloud system user by their UUID.

```bash
jam get-user [USER_ID] [--full]
```

**Options:**
- `USER_ID` - A valid UUID for a JumpCloud user
- `--full` - Display all available fields

**Examples:**
```bash
jam get-user 685cb0f6ef36c7bd8ac56c24
jam get-user 685cb0f6ef36c7bd8ac56c24 --full
```

#### `find-user`
Find a JumpCloud user's UUID by their email address.

```bash
jam find-user [EMAIL]
```

**Examples:**
```bash
jam find-user user@example.com
```

### System Commands

#### `list-systems`
List all systems in JumpCloud.

```bash
jam list-systems [OPTIONS]
```

**Options:**
- `--filter` - Filter using JumpCloud's filter syntax (e.g., `osFamily:$eq:Windows`). Can be used multiple times.
- `--os` - Filter systems by operating system (e.g., `Windows`, `Mac OS X`, or `Ubuntu`)
- `--os-family` - Filter systems by OS family (`windows`, `darwin`, or `linux`)
- `--csv FILE` - Export results to a CSV file

**Examples:**
```bash
jam list-systems
jam list-systems --os-family darwin
jam list-systems --os Windows
jam list-systems --filter 'osFamily:$eq:Windows'
jam list-systems --csv systems.csv
```

#### `get-system`
Get a JumpCloud system by its UUID.

```bash
jam get-system [SYSTEM_ID] [--full]
```

**Options:**
- `SYSTEM_ID` - A valid UUID for a JumpCloud system
- `--full` - Display all available fields

**Examples:**
```bash
jam get-system 69879fa9b5be2f2184d700da
jam get-system 69879fa9b5be2f2184d700da --full
```

#### `find-system`
Find a JumpCloud system's UUID by its hostname or serial number.

```bash
jam find-system [QUERY]
```

**Examples:**
```bash
jam find-system DESKTOP-ABC123
jam find-system C02XG123ABC
```

#### `fde-key`
Retrieve the full disk encryption key for a system.

```bash
jam fde-key [SYSTEM_ID]
```

**Examples:**
```bash
jam fde-key 69879fa9b5be2f2184d700da
```

#### `bound-systems`
Find all systems bound to a JumpCloud user.

```bash
jam bound-systems [USER_ID]
```

**Examples:**
```bash
jam bound-systems 685cb0f6ef36c7bd8ac56c24
```

## Piping Commands

Commands support Unix pipes, allowing you to chain operations:

```bash
# Find a user and get their details
jam find-user user@example.com | jam get-user

# Find a user and list their bound systems
jam find-user user@example.com | jam bound-systems

# Find a system and get its FDE key
jam find-system DESKTOP-ABC123 | jam fde-key
```

## Configuration

Configuration is stored in `pyproject.toml` under `[tool.jam]`:

| Setting | Description | Default |
|---------|-------------|---------|
| `api_url` | JumpCloud API base URL | `https://console.jumpcloud.com/api` |
| `oauth_url` | JumpCloud OAuth token URL | `https://admin-oauth.id.jumpcloud.com/oauth2/token` |
| `timeout` | HTTP request timeout (seconds) | `10` |
| `limit` | Maximum results per API request | `100` |
| `local_tz` | Timezone for displaying timestamps | `US/Eastern` |

### Customizing Output Fields

You can customize which fields are displayed in console output and CSV exports by modifying the field mappings in `pyproject.toml`:

```toml
[tool.jam.console_user_fields]
"ID" = "id"
"State" = "pretty_state"
"Email" = "email"
"Employee Type" = "employee_type"

[tool.jam.csv_user_fields]
"ID" = "id"
"State" = "state"
"Email" = "email"
```

## License

See [LICENSE](LICENSE) for details.

