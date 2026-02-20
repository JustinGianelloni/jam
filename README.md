# JAM - JumpCloud Admin Manager

A command-line interface for managing JumpCloud users and systems.

## Features

- List and search JumpCloud system users
- List and search JumpCloud systems
- Retrieve full disk encryption (FDE) keys
- Find systems bound to specific users
- Find users bound to specific systems
- Export data to CSV files
- Output full JSON models to console (pipe to file with `>`)
- Smart piping support with automatic output format detection
- Batch operations - process multiple resources in a single command
- Concurrent API requests for improved performance
- Optional 1Password integration for credential management

## Prerequisites

- macOS or Linux
- Git
- Python 3.13+
- JumpCloud Admin OAuth credentials (Client ID and Client Secret)
- [1Password CLI](https://developer.1password.com/docs/cli/) (optional, for credential storage)

## Installation

Run the installer directly:
```bash
curl -fsSL https://raw.githubusercontent.com/JustinGianelloni/jam/main/install.sh | bash
```

The script will:
- Install required dependencies (`jq`, `uv`, `fzf`) using your system's package manager
- Clone the repository to `~/.local/share/jam`
- Download the default configuration to `~/.config/jam/config.json`
- Optionally configure 1Password credential references
- Add a `jam` alias to your shell configuration

After installation, reload your shell or run:
```bash
source ~/.zshrc  # or ~/.bashrc for Bash users
```

If not using 1Password, manually configure your credentials in a `.env` file in the project root:
```bash
JAM_CLIENT_ID=your-client-id
JAM_CLIENT_SECRET=your-client-secret
```

## Updating

JAM automatically checks for updates once per day. When an update is available, you'll see a notification:

```
📦 Update available: v0.2.0 (current: v0.1.3)
   Run 'jam update' to install the latest version.
```

To update manually:
```bash
jam update
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
- `-j`, `--json` - Return full JSON model of the user(s)
- `--csv FILE` - Export results to a CSV file

**Examples:**
```bash
# List all users (table format)
jam users list

# List activated users
jam users list --state ACTIVATED

# List users by department and state
jam users list --department Engineering --state ACTIVATED

# List users with custom filter
jam users list --filter 'employeeType:$eq:Contractor'

# Export to CSV
jam users list --csv users.csv

# Get full JSON for all users
jam users list --json

# Pipe user IDs to another command
jam users list --state ACTIVATED | jam users get --json
```

#### `users get`
Get one or more JumpCloud system users by their UUID(s).

```bash
jam users get [USER_ID...] [OPTIONS]
```

**Options:**
- `USER_ID` - One or more valid UUIDs for JumpCloud users (space-separated or via pipe)
- `-j`, `--json` - Return full JSON model of the user(s)

**Examples:**
```bash
# Get a single user
jam users get 685cb0f6ef36c7bd8ac56c24

# Get multiple users
jam users get 685cb0f6ef36c7bd8ac56c24 789cb0f6ef36c7bd8ac56c25

# Get user details in JSON format
jam users get 685cb0f6ef36c7bd8ac56c24 --json
jam users get 685cb0f6ef36c7bd8ac56c24 -j > user.json

# Get multiple users via pipe
echo -e "685cb0f6ef36c7bd8ac56c24\n789cb0f6ef36c7bd8ac56c25" | jam users get
```

#### `users find`
Find a JumpCloud user's UUID by their email address.

```bash
jam users find [EMAIL] [OPTIONS]
```

**Options:**
- `EMAIL` - A valid email address for a JumpCloud user
- `-j`, `--json` - Return full JSON model of the user(s)

**Examples:**
```bash
# Find user and display ID
jam users find user@example.com

# Find user and display full JSON details
jam users find user@example.com --json
```

#### `users bound-systems`
Find all systems bound to a JumpCloud user.

```bash
jam users bound-systems [USER_ID] [OPTIONS]
```

**Options:**
- `USER_ID` - A valid UUID for a JumpCloud user
- `-j`, `--json` - Return full JSON model of the system(s)

**Examples:**
```bash
# List bound systems as a table
jam users bound-systems 685cb0f6ef36c7bd8ac56c24

# Get full JSON details of bound systems
jam users bound-systems 685cb0f6ef36c7bd8ac56c24 --json
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
- `-j`, `--json` - Return full JSON model of the system(s)
- `--csv FILE` - Export results to a CSV file

**Examples:**
```bash
# List all systems (table format)
jam systems list

# List systems by OS family
jam systems list --os-family darwin

# List systems by specific OS
jam systems list --os Windows

# List systems with custom filter
jam systems list --filter 'osFamily:$eq:Windows'

# Export to CSV
jam systems list --csv systems.csv

# Get full JSON for all systems
jam systems list --json

# Pipe system IDs to another command
jam systems list --os-family darwin | jam systems get --json
```

#### `systems get`
Get one or more JumpCloud systems by their UUID(s).

```bash
jam systems get [SYSTEM_ID...] [OPTIONS]
```

**Options:**
- `SYSTEM_ID` - One or more valid UUIDs for JumpCloud systems (space-separated or via pipe)
- `-j`, `--json` - Return full JSON model of the system(s)

**Examples:**
```bash
# Get a single system
jam systems get 69879fa9b5be2f2184d700da

# Get multiple systems
jam systems get 69879fa9b5be2f2184d700da 79879fa9b5be2f2184d700db

# Get system details in JSON format
jam systems get 69879fa9b5be2f2184d700da --json
jam systems get 69879fa9b5be2f2184d700da -j > system.json

# Get multiple systems via pipe
echo -e "69879fa9b5be2f2184d700da\n79879fa9b5be2f2184d700db" | jam systems get
```

#### `systems find`
Find a JumpCloud system's UUID by its hostname or serial number.

```bash
jam systems find [QUERY] [OPTIONS]
```

**Options:**
- `QUERY` - A hostname or serial number to search for
- `-j`, `--json` - Return full JSON model of the system(s)

**Examples:**
```bash
# Find system and display ID
jam systems find DESKTOP-ABC123
jam systems find C02XG123ABC

# Find system and display full JSON details
jam systems find DESKTOP-ABC123 --json
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

#### `systems bound-users`
Find all users bound to a JumpCloud system.

```bash
jam systems bound-users [SYSTEM_ID] [OPTIONS]
```

**Options:**
- `SYSTEM_ID` - A valid UUID for a JumpCloud system
- `-j`, `--json` - Return full JSON model of the user(s)

**Examples:**
```bash
# List bound users as a table
jam systems bound-users 69879fa9b5be2f2184d700da

# Get full JSON details of bound users
jam systems bound-users 69879fa9b5be2f2184d700da --json
```

## Piping and Command Chaining

JAM intelligently detects when output is being piped and automatically formats data for easy command chaining. When piped, commands output resource IDs (one per line) instead of formatted tables, making them perfect for input to other commands.

### Basic Piping Examples

```bash
# Find a user and get their details
jam users find user@example.com | jam users get

# Find a user and list their bound systems
jam users find user@example.com | jam users bound-systems

# Find a system and get its FDE key
jam systems find DESKTOP-ABC123 | jam systems fde-key

# Find a system and list its bound users
jam systems find DESKTOP-ABC123 | jam systems bound-users
```

### Advanced Piping Examples

```bash
# Get full JSON details for all activated users
jam users list --state ACTIVATED | jam users get --json

# Get details for all macOS systems
jam systems list --os-family darwin | jam systems get

# Export all Windows systems to JSON files
jam systems list --os-family windows | jam systems get --json > windows-systems.json

# Get FDE keys for all systems in a department's users' computers
jam users list --department Engineering | jam users bound-systems | jam systems fde-key

# Find all systems bound to contractors
jam users list --filter 'employeeType:$eq:Contractor' | jam users bound-systems

# Get detailed info for multiple specific users
echo -e "685cb0f6ef36c7bd8ac56c24\n789cb0f6ef36c7bd8ac56c25" | jam users get --json
```

### How Piping Works

- **When output is piped** (e.g., `jam users list | ...`):
  - Resource commands output IDs only, one per line
  - Perfect for chaining into other commands
  - No visual formatting or tables

- **When output is NOT piped** (e.g., `jam users list`):
  - Displays rich formatted tables with multiple columns
  - Easy to read in the terminal
  - Shows total count and relevant fields

- **With `--json` flag**:
  - Outputs complete JSON model(s)
  - When piped: outputs line-delimited JSON for multiple results
  - When not piped: pretty-printed JSON with indentation
  - Can be redirected to files with `>`

### Batch Operations

Many commands now accept multiple IDs, enabling batch operations:

```bash
# Get multiple users at once
jam users get 685cb0f6ef36c7bd8ac56c24 789cb0f6ef36c7bd8ac56c25 812cb0f6ef36c7bd8ac56c26

# Get multiple systems at once
jam systems get 69879fa9b5be2f2184d700da 79879fa9b5be2f2184d700db

# Process results from a list command
jam users list --department Engineering | jam users get --json
```

## Configuration

Configuration is stored in `~/.config/jam/config.json`:

| Setting | Description | Default |
|---------|-------------|---------|
| `api_url` | JumpCloud API base URL | `https://console.jumpcloud.com/api` |
| `oauth_url` | JumpCloud OAuth token URL | `https://admin-oauth.id.jumpcloud.com/oauth2/token` |
| `timeout` | HTTP request timeout (seconds) | `10` |
| `limit` | Maximum results per API request | `100` |
| `local_tz` | Timezone for displaying timestamps | `US/Eastern` |

### Customizing Output Fields

You can customize which fields are displayed in console output and CSV exports by modifying the field mappings in `config.json`:

```json
{
  "jam": {
    "console_user_fields": {
      "ID": "id",
      "State": "pretty_state",
      "Email": "email",
      "Employee Type": "employee_type"
    },
    "csv_user_fields": {
      "ID": "id",
      "State": "state",
      "Email": "email"
    }
  }
}
```

## License

See [LICENSE](LICENSE) for details.

