# JAM - JumpCloud Admin Manager

A command-line interface for managing JumpCloud users and systems.

## Features

- List and search JumpCloud system users
- List and search JumpCloud systems
- Retrieve full disk encryption (FDE) keys
- Find systems bound to specific users
- Find users bound to specific systems
- List and manage user group memberships
- List and search JumpCloud applications and their associated groups
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
- JumpCloud Admin OAuth credentials (Client ID and Client Secret) -
  see [Generating JumpCloud API Credentials](#generating-jumpcloud-api-credentials)
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

User commands are accessed via the `user` subcommand group.

#### `user list`

List all system users in JumpCloud.

```bash
jam user list [OPTIONS]
```

**Options:**

- `--filter` - Filter using JumpCloud's filter syntax (e.g., `employeeType:$eq:Contractor`). Can be used multiple times.
- `--department` - Filter users by department (e.g., `Engineering`)
- `--cost-center` - Filter users by cost center (e.g., `Data Engineering`)
- `--title` - Filter users by job title (e.g., `Data Engineer`)
- `--state` - Filter users by state (`ACTIVATED`, `SUSPENDED`, or `STAGED`)
- `--type` - Filter users by employee type (e.g., `Full Time`, `Contractor`, or `Service`)
- `-j`, `--json` - Return full JSON model of the user(s)
- `--csv FILE` - Export results to a CSV file

**Examples:**

```bash
# List all users (table format)
jam user list

# List activated users
jam user list --state ACTIVATED

# List users by department and state
jam user list --department Engineering --state ACTIVATED

# List contractors
jam user list --type Contractor

# List users with custom filter
jam user list --filter 'employeeType:$eq:Contractor'

# Export to CSV
jam user list --csv users.csv

# Get full JSON for all users
jam user list --json

# Pipe user IDs to another command
jam user list --state ACTIVATED | jam user get --json
```

#### `user get`

Get one or more JumpCloud system users by their UUID(s).

```bash
jam user get [USER_ID...] [OPTIONS]
```

**Options:**

- `USER_ID` - One or more valid UUIDs for JumpCloud users (space-separated or via pipe)
- `-j`, `--json` - Return full JSON model of the user(s)

**Examples:**

```bash
# Get a single user
jam user get 685cb0f6ef36c7bd8ac56c24

# Get multiple users
jam user get 685cb0f6ef36c7bd8ac56c24 789cb0f6ef36c7bd8ac56c25

# Get user details in JSON format
jam user get 685cb0f6ef36c7bd8ac56c24 --json
jam user get 685cb0f6ef36c7bd8ac56c24 -j > user.json

# Get multiple users via pipe
echo -e "685cb0f6ef36c7bd8ac56c24\n789cb0f6ef36c7bd8ac56c25" | jam user get
```

#### `user find`

Find a JumpCloud user's UUID by their email address.

```bash
jam user find [EMAIL] [OPTIONS]
```

**Options:**

- `EMAIL` - A valid email address for a JumpCloud user
- `-j`, `--json` - Return full JSON model of the user(s)

**Examples:**

```bash
# Find user and display ID
jam user find user@example.com

# Find user and display full JSON details
jam user find user@example.com --json
```

#### `user bound-systems`

Find all systems bound to a JumpCloud user.

```bash
jam user bound-systems [USER_ID] [OPTIONS]
```

**Options:**

- `USER_ID` - A valid UUID for a JumpCloud user
- `-j`, `--json` - Return full JSON model of the system(s)

**Examples:**

```bash
# List bound systems as a table
jam user bound-systems 685cb0f6ef36c7bd8ac56c24

# Get full JSON details of bound systems
jam user bound-systems 685cb0f6ef36c7bd8ac56c24 --json
```

### System Commands

System commands are accessed via the `system` subcommand group.

#### `system list`

List all systems in JumpCloud.

```bash
jam system list [OPTIONS]
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
jam system list

# List systems by OS family
jam system list --os-family darwin

# List systems by specific OS
jam system list --os Windows

# List systems with custom filter
jam system list --filter 'osFamily:$eq:Windows'

# Export to CSV
jam system list --csv systems.csv

# Get full JSON for all systems
jam system list --json

# Pipe system IDs to another command
jam system list --os-family darwin | jam system get --json
```

#### `system get`

Get one or more JumpCloud systems by their UUID(s).

```bash
jam system get [SYSTEM_ID...] [OPTIONS]
```

**Options:**

- `SYSTEM_ID` - One or more valid UUIDs for JumpCloud systems (space-separated or via pipe)
- `-j`, `--json` - Return full JSON model of the system(s)

**Examples:**

```bash
# Get a single system
jam system get 69879fa9b5be2f2184d700da

# Get multiple systems
jam system get 69879fa9b5be2f2184d700da 79879fa9b5be2f2184d700db

# Get system details in JSON format
jam system get 69879fa9b5be2f2184d700da --json
jam system get 69879fa9b5be2f2184d700da -j > system.json

# Get multiple systems via pipe
echo -e "69879fa9b5be2f2184d700da\n79879fa9b5be2f2184d700db" | jam system get
```

#### `system find`

Find a JumpCloud system's UUID by its hostname or serial number.

```bash
jam system find [QUERY] [OPTIONS]
```

**Options:**

- `QUERY` - A hostname or serial number to search for
- `-j`, `--json` - Return full JSON model of the system(s)

**Examples:**

```bash
# Find system and display ID
jam system find DESKTOP-ABC123
jam system find C02XG123ABC

# Find system and display full JSON details
jam system find DESKTOP-ABC123 --json
```

#### `system fde-key`

Retrieve the full disk encryption key for a system.

```bash
jam system fde-key [SYSTEM_ID]
```

**Examples:**

```bash
jam system fde-key 69879fa9b5be2f2184d700da
```

#### `system bound-users`

Find all users bound to a JumpCloud system.

```bash
jam system bound-users [SYSTEM_ID] [OPTIONS]
```

**Options:**

- `SYSTEM_ID` - A valid UUID for a JumpCloud system
- `-j`, `--json` - Return full JSON model of the user(s)

**Examples:**

```bash
# List bound users as a table
jam system bound-users 69879fa9b5be2f2184d700da

# Get full JSON details of bound users
jam system bound-users 69879fa9b5be2f2184d700da --json
```

### Group Commands

Group commands are accessed via the `group` subcommand group.

#### `group list`

List all user groups in JumpCloud.

```bash
jam group list [OPTIONS]
```

**Options:**

- `--filter` - Filter using JumpCloud's v2 filter syntax (e.g., `name:eq:Engineering`). Can be used multiple times.
- `--name` - Filter groups by name (e.g., `Engineering`)
- `-j`, `--json` - Return full JSON model of the group(s)
- `--csv FILE` - Export results to a CSV file

**Examples:**

```bash
# List all user groups (table format)
jam group list

# List groups filtered by name
jam group list --name Engineering

# List groups with custom filter
jam group list --filter 'name:search:Eng'

# Export to CSV
jam group list --csv groups.csv

# Get full JSON for all groups
jam group list --json
```

#### `group member list`

List all members of one or more JumpCloud user groups.

```bash
jam group member list [GROUP_ID...] [OPTIONS]
```

**Options:**

- `GROUP_ID` - One or more valid UUIDs for JumpCloud user groups (space-separated or via pipe)
- `-j`, `--json` - Return full JSON model of the group members
- `--csv FILE` - Export results to a CSV file

**Examples:**

```bash
# List group members as a table
jam group member list 689e1335e907ee000186085f

# List members across multiple groups
jam group member list 689e1335e907ee000186085f 789e1335e907ee000186085f

# Get full JSON details of group members
jam group member list 689e1335e907ee000186085f --json

# Export group members to CSV
jam group member list 689e1335e907ee000186085f --csv members.csv
```

#### `group member add`

Add one or more users to one or more JumpCloud user groups. Displays a confirmation prompt before making any changes.

```bash
jam group member add [OPTIONS]
```

**Options:**

- `--group-id` - A valid UUID for a JumpCloud group
- `-n`, `--name` - A valid name for a JumpCloud group
- `--group-csv FILE` - A CSV list of group IDs to update
- `-u`, `--user` - A valid UUID for a JumpCloud user
- `-e`, `--email` - A valid email address for a JumpCloud user
- `--user-csv FILE` - A CSV list of user IDs to add

Exactly one group selector (`--group-id`, `--name`, or `--group-csv`) and one user selector (`--user`, `--email`, or `--user-csv`) must be provided.

**Examples:**

```bash
# Add a single user to a single group by ID
jam group member add --group-id 689e1335e907ee000186085f --user 685cb0f6ef36c7bd8ac56c24

# Add a user to a group by name and email
jam group member add --name Engineering --email user@example.com

# Add multiple users (via CSV) to multiple groups (via CSV)
jam group member add --group-csv groups.csv --user-csv users.csv

# Add a single user to multiple groups via CSV
jam group member add --group-csv groups.csv --email user@example.com
```

### Application Commands

Application commands are accessed via the `application` subcommand group.

#### `application list`

List all applications in JumpCloud.

```bash
jam application list [OPTIONS]
```

**Options:**

- `--filter` - Filter using JumpCloud's filter syntax (e.g., `name:$eq:GitHub Prod`). Can be used multiple times.
- `--name` - Filter applications by name (e.g., `GitHub Prod`)
- `-a`, `--active` - Show only active applications
- `-i`, `--inactive` - Show only inactive applications
- `-j`, `--json` - Return full JSON model of the application(s)
- `--csv FILE` - Export results to a CSV file

**Examples:**

```bash
# List all applications (table format)
jam application list

# List applications filtered by name
jam application list --name "GitHub Prod"

# List only active applications
jam application list --active

# List only inactive applications
jam application list --inactive

# Export to CSV
jam application list --csv apps.csv

# Get full JSON for all applications
jam application list --json
```

#### `application group list`

List all user groups associated with a JumpCloud application.

```bash
jam application group list [APP_ID] [OPTIONS]
```

**Options:**

- `APP_ID` - A valid UUID for a JumpCloud application
- `-j`, `--json` - Return full JSON model of the group(s)
- `--csv FILE` - Export results to a CSV file

**Examples:**

```bash
# List groups associated with an application
jam application group list 64dfcc79523de4972dce15f0

# Get full JSON details of associated groups
jam application group list 64dfcc79523de4972dce15f0 --json

# Export associated groups to CSV
jam application group list 64dfcc79523de4972dce15f0 --csv app-groups.csv
```

### Config Commands

Config commands are accessed via the `config` subcommand group.

#### `config path`

Show the path to the configuration file.

```bash
jam config path
```

**Examples:**

```bash
# Display config file location
jam config path
```

#### `config show`

Display the current configuration.

```bash
jam config show
```

**Examples:**

```bash
# Show current configuration with syntax highlighting
jam config show
```

#### `config reset`

Reset the configuration to defaults.

```bash
jam config reset [OPTIONS]
```

**Options:**

- `-f`, `--force` - Skip confirmation prompt
- `-q`, `--quiet` - Suppress console output

**Examples:**

```bash
# Reset config with confirmation prompt
jam config reset

# Reset config without confirmation
jam config reset --force

# Reset config silently
jam config reset --force --quiet
```

## Piping and Command Chaining

JAM intelligently detects when output is being piped and automatically formats data for easy command chaining. When
piped, commands output resource IDs (one per line) instead of formatted tables, making them perfect for input to other
commands.

### Basic Piping Examples

```bash
# Find a user and get their details
jam user find user@example.com | jam user get

# Find a user and list their bound systems
jam user find user@example.com | jam user bound-systems

# Find a system and get its FDE key
jam system find DESKTOP-ABC123 | jam system fde-key

# Find a system and list its bound users
jam system find DESKTOP-ABC123 | jam system bound-users
```

### Advanced Piping Examples

```bash
# Get full JSON details for all activated users
jam user list --state ACTIVATED | jam user get --json

# Get details for all macOS systems
jam system list --os-family darwin | jam system get

# Export all Windows systems to JSON files
jam system list --os-family windows | jam system get --json > windows-systems.json

# Get FDE keys for all systems in a department's users' computers
jam user list --department Engineering | jam user bound-systems | jam system fde-key

# Find all systems bound to contractors
jam user list --type Contractor | jam user bound-systems

# Get detailed info for multiple specific users
echo -e "685cb0f6ef36c7bd8ac56c24\n789cb0f6ef36c7bd8ac56c25" | jam user get --json
```

### How Piping Works

- **When output is piped** (e.g., `jam user list | ...`):
    - Resource commands output IDs only, one per line
    - Perfect for chaining into other commands
    - No visual formatting or tables

- **When output is NOT piped** (e.g., `jam user list`):
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
jam user get 685cb0f6ef36c7bd8ac56c24 789cb0f6ef36c7bd8ac56c25 812cb0f6ef36c7bd8ac56c26

# Get multiple systems at once
jam system get 69879fa9b5be2f2184d700da 79879fa9b5be2f2184d700db

# Process results from a list command
jam user list --department Engineering | jam user get --json

# List members of multiple groups at once
jam group member list 689e1335e907ee000186085f 789e1335e907ee000186085f
```

## Configuration

Configuration is stored in `~/.config/jam/config.json`:

| Setting     | Description                        | Default                                             |
|-------------|------------------------------------|-----------------------------------------------------|
| `api_url`   | JumpCloud API base URL             | `https://console.jumpcloud.com/api`                 |
| `oauth_url` | JumpCloud OAuth token URL          | `https://admin-oauth.id.jumpcloud.com/oauth2/token` |
| `timeout`   | HTTP request timeout (seconds)     | `10`                                                |
| `limit`     | Maximum results per API request    | `100`                                               |
| `local_tz`  | Timezone for displaying timestamps | `US/Eastern`                                        |

### Customizing Output Fields

You can customize which fields are displayed in console output and CSV exports by modifying the field mappings in
`config.json`. The following field mapping keys are supported:

| Key                     | Controls                                      |
|-------------------------|-----------------------------------------------|
| `console_user_fields`   | Columns shown in the terminal for users       |
| `csv_user_fields`       | Columns written to CSV for users              |
| `console_system_fields` | Columns shown in the terminal for systems     |
| `csv_system_fields`     | Columns written to CSV for systems            |
| `console_group_fields`  | Columns shown in the terminal for groups      |
| `csv_group_fields`      | Columns written to CSV for groups             |
| `console_app_fields`    | Columns shown in the terminal for applications |
| `csv_app_fields`        | Columns written to CSV for applications       |

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
    },
    "console_app_fields": {
      "ID": "id",
      "Display Name": "display_label",
      "Active": "active"
    },
    "csv_app_fields": {
      "ID": "id",
      "Display Name": "display_label",
      "Active": "active"
    }
  }
}
```

## Generating JumpCloud API Credentials

JAM requires OAuth credentials (Client ID and Client Secret) from a JumpCloud Service Account to authenticate with the
JumpCloud API.

### Creating a Service Account

1. **Log in to the JumpCloud Admin Portal** at [https://console.jumpcloud.com](https://console.jumpcloud.com)

2. **Navigate to Service Accounts**
    - Go to **Settings** (gear icon) → **Service Accounts**
    - Or navigate directly to: `https://console.jumpcloud.com/#/settings/service-accounts`

3. **Create a New Service Account**
    - Click **+ Add Service Account**
    - Enter a descriptive **Name** (e.g., "JAM CLI Tool")
    - Optionally add a **Description**
    - Click **Create**

4. **Generate API Credentials**
    - After creating the service account, click on it to view details
    - Under **API Keys**, click **Generate New Key**
    - **Important:** Copy and securely store both the **Client ID** and **Client Secret** immediately. The Client Secret
      will only be shown once.

5. **Assign Permissions**
    - Service accounts need appropriate permissions to access resources
    - Under **Permissions**, assign the required access levels:
        - **Read Users** - Required for user listing and search operations
        - **Read Systems** - Required for system listing and search operations
        - **Read User Groups** - Required for group listing operations
        - **Write User Groups** - Required for `group member add`
        - **Read System Associations** - Required for bound-users and bound-systems commands
        - **Read FDE Keys** - Required for the fde-key command
        - **Read Applications** - Required for application listing operations
    - Click **Save** to apply permissions

### Configuring JAM with Your Credentials

Once you have your Client ID and Client Secret, configure JAM using one of these methods:

#### Option 1: Environment File (Recommended for personal use)

Create a `.env` file in the JAM config directory (`~/.config/jam/.env`):

```bash
JAM_CLIENT_ID=your-client-id-here
JAM_CLIENT_SECRET=your-client-secret-here
```

#### Option 2: 1Password Integration (Recommended for teams)

During installation, JAM can be configured to use 1Password secret references. Store your credentials in 1Password and
reference them:

```bash
JAM_CLIENT_ID=op://vault/item/client_id
JAM_CLIENT_SECRET=op://vault/item/client_secret
```

#### Option 3: Environment Variables

Export the credentials directly in your shell:

```bash
export JAM_CLIENT_ID=your-client-id-here
export JAM_CLIENT_SECRET=your-client-secret-here
```

### Security Best Practices

- **Never commit credentials** to version control
- **Use 1Password** or another secrets manager for team environments
- **Rotate credentials** periodically
- **Use least privilege** - only grant the permissions your workflows require
- **Monitor usage** - review service account activity in the JumpCloud Admin Portal

For more information on JumpCloud Service Accounts, see
the [official documentation](https://jumpcloud.com/support/service-account-for-apis).

## License

See [LICENSE](LICENSE) for details.
