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
   JAM_CLIENT_ID=your-client-id
   JAM_CLIENT_SECRET=your-client-secret
   ```

## Commands

### User Commands

User commands are accessed via the `users` subcommand group.

#### `users list`
List all system users in JumpCloud.

```bash
jam users list [OPTIONS]
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
jam users list
jam users list --state ACTIVATED
jam users list --department Engineering --state ACTIVATED
jam users list --filter 'employeeType:$eq:Contractor'
jam users list --csv users.csv
```

#### `users get`
Get a JumpCloud system user by their UUID.

```bash
jam users get [USER_ID] [OPTIONS]
```

**Options:**
- `USER_ID` - A valid UUID for a JumpCloud user
- `--full` - Display all available fields
- `--json FILE` - Export user to a JSON file

**Examples:**
```bash
jam users get 685cb0f6ef36c7bd8ac56c24
jam users get 685cb0f6ef36c7bd8ac56c24 --full
jam users get 685cb0f6ef36c7bd8ac56c24 --json user.json
```

#### `users find`
Find a JumpCloud user's UUID by their email address.

```bash
jam users find [EMAIL]
```

**Examples:**
```bash
jam users find user@example.com
```

### System Commands

System commands are accessed via the `systems` subcommand group.

#### `systems list`
List all systems in JumpCloud.

```bash
jam systems list [OPTIONS]
```

**Options:**
- `--filter` - Filter using JumpCloud's filter syntax (e.g., `osFamily:$eq:Windows`). Can be used multiple times.
- `--os` - Filter systems by operating system (e.g., `Windows`, `Mac OS X`, or `Ubuntu`)
- `--os-family` - Filter systems by OS family (`windows`, `darwin`, or `linux`)
- `--csv FILE` - Export results to a CSV file

**Examples:**
```bash
jam systems list
jam systems list --os-family darwin
jam systems list --os Windows
jam systems list --filter 'osFamily:$eq:Windows'
jam systems list --csv systems.csv
```

#### `systems get`
Get a JumpCloud system by its UUID.

```bash
jam systems get [SYSTEM_ID] [OPTIONS]
```

**Options:**
- `SYSTEM_ID` - A valid UUID for a JumpCloud system
- `--full` - Display all available fields

**Examples:**
```bash
jam systems get 69879fa9b5be2f2184d700da
jam systems get 69879fa9b5be2f2184d700da --full
```

#### `systems find`
Find a JumpCloud system's UUID by its hostname or serial number.

```bash
jam systems find [QUERY]
```

**Examples:**
```bash
jam systems find DESKTOP-ABC123
jam systems find C02XG123ABC
```

#### `systems fde-key`
Retrieve the full disk encryption key for a system.

```bash
jam systems fde-key [SYSTEM_ID]
```

**Examples:**
```bash
jam systems fde-key 69879fa9b5be2f2184d700da
```

#### `systems bound`
Find all systems bound to a JumpCloud user.

```bash
jam systems bound [USER_ID]
```

**Examples:**
```bash
jam systems bound 685cb0f6ef36c7bd8ac56c24
```

## Piping Commands

Commands support Unix pipes, allowing you to chain operations:

```bash
# Find a user and get their details
jam users find user@example.com | jam users get

# Find a user and list their bound systems
jam users find user@example.com | jam systems bound

# Find a system and get its FDE key
jam systems find DESKTOP-ABC123 | jam systems fde-key
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

