# jam

A command-line interface for JumpCloud, written in Go.

## Features

- **User management** - list, get, find, and view bound systems
- **System management** - list, get, find, and view bound users
- **Group management** - list groups and members
- **Application management** - list apps and assigned groups
- **Piping support** - chain commands together (`jam user list | jam user get`)
- **Multiple output formats** - tables, JSON (`--json`), and CSV (`--csv path`)
- **Concurrent API requests** - fast bulk lookups
- **1Password integration** - secure credential storage via the 1Password SDK

## Prerequisites

- macOS or Linux
- [JumpCloud](https://jumpcloud.com) admin account with API OAuth credentials
- [1Password](https://1password.com) desktop app (for credential management)

## Installation

```bash
curl -fsSL https://raw.githubusercontent.com/JustinGianelloni/jam/main/install.sh | bash
```

The installer will:
1. Download the latest `jam` binary to `~/.local/bin`
2. Create `~/.config/jam/config.json`
3. Optionally configure 1Password credential references

## Configuration

Configuration is stored at `~/.config/jam/config.json`. Credentials can be provided in three ways:

### 1Password (recommended)

Set the following keys in `config.json`:

| Key | Description |
|-----|-------------|
| `OP_ACCOUNT` | Your 1Password account name |
| `OP_CLIENT_ID_URI` | Secret reference for the OAuth Client ID (e.g. `op://vault/item/field`) |
| `OP_CLIENT_SECRET_URI` | Secret reference for the OAuth Client Secret |

The install script configures these interactively using the `op` CLI.

### Environment variables

```bash
export JAM_CLIENT_ID="your-client-id"
export JAM_CLIENT_SECRET="your-client-secret"
```

### .env file

Create `~/.config/jam/.env`:

```
JAM_CLIENT_ID=your-client-id
JAM_CLIENT_SECRET=your-client-secret
```

## Commands

### Users

```bash
jam user list                       # List all users
jam user list -s ACTIVATED          # Filter by state
jam user list -d Engineering        # Filter by department
jam user get <id> [<id>...]         # Get users by ID
jam user find <term>                # Search users (all fields)
jam user find -e <term>             # Search by email
jam user bound-systems <id>         # List systems bound to a user
```

### Systems

```bash
jam system list                     # List all systems
jam system list -m                  # List only macOS devices
jam system list -w                  # List only Windows devices
jam system get <id> [<id>...]       # Get systems by ID
jam system find <term>              # Search systems (all fields)
jam system find -s <term>           # Search by serial number
jam system bound-users <id>         # List users bound to a system
```

### Groups

```bash
jam group list                      # List all groups
jam group list -n Engineering       # Filter by name
jam group member list <id>          # List members of a group
```

### Applications

```bash
jam app list                        # List all applications
jam app list -n Slack               # Filter by name
jam app group list <id>             # List groups assigned to an app
```

### Output options

Most list commands support:

- `--json` - output as JSON
- `--csv <path>` - export to CSV file
- Show/hide columns with flags like `-D` (department), `-C` (cost center), `-J` (job title), `-S` (state), `-T` (employee type), `-I` (remote IP), `-H` (hostname)

### Piping

When output is piped, jam emits plain IDs (one per line) instead of tables:

```bash
jam user list -d Engineering | jam user bound-systems
jam group list -n Admins | jam group member list
```

## JumpCloud API credentials

1. In the JumpCloud Admin Console, create an API Client under **Management** > **API Clients**
2. Grant the client the required permissions (read access to users, systems, groups, applications)
3. Save the **Client ID** and **Client Secret**

## License

[MIT](LICENSE)
