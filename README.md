# Custom FastMCP Servers

A collection of custom Model Context Protocol (MCP) servers built with Python (`FastMCP`) to integrate various self-hosted media and personal services with AI agents (such as Hermes Agent).

## Included Servers

1. **Radarr** (`radarr_mcp.py`) - Full Radarr v3 API: movie CRUD, TMDB/IMDB lookup, release search & force-grab, queue management, manual import, history, blocklist, missing/cutoff monitoring, config resources, system commands.
2. **Sonarr** (`sonarr_mcp.py`) - Manage TV series and calendar.
3. **Prowlarr** (`prowlarr_mcp.py`) - Manage indexers and search.
4. **Seerr / Overseerr** (`seerr_mcp.py`) - Media requests and search (includes `seerr_request_movie`).
5. **Jellyfin** (`jellyfin_mcp.py`) - Jellyfin library search and metadata.
6. **qBittorrent** (`qbittorrent_mcp.py`) - Active torrents monitoring.
7. **Gramps Web** (`gramps_mcp_server.py`) - Genealogy records and search.

## Requirements

- Python 3.10+
- `mcp` (FastMCP)
- `httpx`

Install dependencies:
```bash
pip install mcp httpx
```

## Configuration

Each server relies on environment variables for URL and API keys/credentials:

- **Radarr**: `RADARR_URL`, `RADARR_API_KEY`
- **Sonarr**: `SONARR_URL`, `SONARR_API_KEY`
- **Prowlarr**: `PROWLARR_URL`, `PROWLARR_API_KEY`
- **Seerr**: `SEERR_URL`, `SEERR_API_KEY`
- **Jellyfin**: `JELLYFIN_URL`, `JELLYFIN_API_KEY`
- **qBittorrent**: `QBIT_URL`
- **Gramps**: `GRAMPS_WEB_URL`, `GRAMPS_WEB_USERNAME`, `GRAMPS_WEB_PASSWORD`

## Radarr Tools (28 total)

### Movie Management
- `radarr_list_movies` — list all movies with images
- `radarr_get_movie_by_id` — get movie details
- `radarr_add_movie` — add new movie (tmdbId, rootPath, quality profile, tags)
- `radarr_update_movie` — update movie fields (monitored, tags, quality profile)
- `radarr_delete_movie` — remove movie (optionally delete files)
- `radarr_get_movie_files` — list downloaded files for a movie
- `radarr_delete_movie_file` — remove specific movie file

### Search & Lookup
- `radarr_lookup_movie_tmdb` — search by TMDB title
- `radarr_lookup_movie_imdb` — search by IMDB title
- `radarr_lookup_movie` — generic lookup (all sources)
- `radarr_parse_title` — parse title from free text/torrent name

### Release Management
- `radarr_get_releases` — all available releases for a movie (quality, size, protocol, age, seeders, rejections)
- `radarr_force_grab_release` — force download a specific release

### Queue Management
- `radarr_get_queue` — download queue with pagination
- `radarr_get_queue_details` — queue filtered by movie
- `radarr_remove_from_queue` — remove single queue item
- `radarr_bulk_remove_from_queue` — remove multiple items
- `radarr_grab_release` — manual grab of queued release
- `radarr_get_queue_status` — overall queue status

### Manual Import
- `radarr_list_manual_import_files` — list files in folder for import
- `radarr_manual_import` — import files manually
- `radarr_import_existing_movie` — import already-downloaded folder

### Wanted / Missing
- `radarr_get_missing_movies` — movies without releases
- `radarr_get_cutoff_unmet` — movies with unmet quality cutoff

### History
- `radarr_get_history` — download history (filterable by movie)
- `radarr_get_history_since` — recent history
- `radarr_mark_as_failed` — re-queue failed download

### Blocklist
- `radarr_get_blocklist` — blocked releases
- `radarr_remove_from_blocklist` — unblock a release

### Configuration
- `radarr_get_quality_profiles` — available quality profiles
- `radarr_get_indexers` — configured indexers
- `radarr_get_download_clients` — download clients (qBittorrent, SABnzbd)
- `radarr_get_root_folders` — disk root folders
- `radarr_get_tags` — available tags
- `radarr_get_languages` — audio languages
- `radarr_get_remote_path_mappings` — remote path mappings

### Commands
- `radarr_run_command` — execute commands (backfill, moviesearch, rescan)
- `radarr_list_commands` — running/completed commands
- `radarr_get_command_status` — command progress/errors

### System
- `radarr_get_system_status` — version, instance info
- `radarr_get_disk_space` — disk usage per folder
