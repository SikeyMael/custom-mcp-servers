# Custom MCP Servers

A collection of custom Python-based Model Context Protocol (MCP) servers compatible with Hermes Agent and any other MCP-compliant AI agent framework.

## Included Servers

- **Gramps Web** (`gramps_mcp_server.py`)
- **Jellyfin** (`jellyfin_mcp.py`)
- **Prowlarr** (`prowlarr_mcp.py`)
- **qBittorrent** (`qbittorrent_mcp.py`)
- **Radarr** (`radarr_mcp.py`)
- **Seerr / Overseerr** (`seerr_mcp.py`)
- **Sonarr** (`sonarr_mcp.py`)

## Usage

Configure them in your MCP client settings (e.g. `config.yaml` for Hermes) pointing to the python interpreter and the corresponding script path, passing the required API keys or URLs via environment variables.