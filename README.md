# Custom MCP Servers

A collection of custom Python-based Model Context Protocol (MCP) servers compatible with Hermes Agent and any other MCP-compliant AI agent framework (built using FastMCP).

---

## 1. Gramps Web (`gramps_mcp_server.py`)
Genealogy database integration.
- **Environment Variables / Parameters:**
  - `GRAMPS_WEB_URL` (str): Base URL of Gramps Web instance.
  - `GRAMPS_WEB_USERNAME` (str): Username for authentication.
  - `GRAMPS_WEB_PASSWORD` (str): Password for authentication.
- **Exposed Tools:**
  - `search_people(query: str)`: Search individuals in Gramps Web by name or query string.
  - `get_person(person_id: str)`: Get detailed information about an individual by ID/handle.
  - `list_families()`: List families in the Gramps database.
  - `get_family(family_id: str)`: Get detailed information about a family by ID/handle.
  - `search_places(query: str)`: Search places by name or query.
  - `list_bookmark_types()`: Get the list of bookmark types/namespaces.
  - `get_bookmarks(namespace: str)`: Get list of bookmarks by namespace.
  - `search_gramps(query: str, type: str = None)`: Search objects in Gramps Web (person, family, event, etc.).

---

## 2. Jellyfin (`jellyfin_mcp.py`)
Media server integration.
- **Environment Variables / Parameters:**
  - `JELLYFIN_URL` (str): Jellyfin server URL.
  - `JELLYFIN_API_KEY` (str): API Key / Access Token.
- **Exposed Tools:**
  - `jellyfin_search(term: str)`: Search items in Jellyfin library.
  - `jellyfin_library_latest()`: Get latest added media items in Jellyfin.
  - `jellyfin_get_items(parent_id: str = "", include_item_types: str = "")`: Get items from Jellyfin with optional parent ID and item types.
  - `jellyfin_get_item_details(item_id: str)`: Get detailed metadata for a specific Jellyfin item ID.
  - `jellyfin_get_users()`: List all Jellyfin users.
  - `jellyfin_system_info()`: Get Jellyfin server system information.

---

## 3. Prowlarr (`prowlarr_mcp.py`)
Indexer management integration.
- **Environment Variables / Parameters:**
  - `PROWLARR_URL` (str): Prowlarr server URL.
  - `PROWLARR_API_KEY` (str): API Key.
- **Exposed Tools:**
  - `prowlarr_list_indexers()`: List all configured indexers in Prowlarr.
  - `prowlarr_search_indexers(query: str, indexer_ids: str = "")`: Search across indexers in Prowlarr.
  - `prowlarr_list_applications()`: List connected applications in Prowlarr (Sonarr, Radarr, etc.).
  - `prowlarr_list_history()`: List search / grab history in Prowlarr.

---

## 4. qBittorrent (`qbittorrent_mcp.py`)
Torrent client integration.
- **Environment Variables / Parameters:**
  - `QBIT_URL` (str): qBittorrent WebUI URL.
- **Exposed Tools:**
  - `qbit_list_torrents()`: List all active torrents in qBittorrent.
  - `qbit_transfer_info()`: Get global transfer info (download/upload speed, etc.).
  - `qbit_pause_torrent(torrent_hash: str)`: Pause a torrent by its hash.
  - `qbittorrent_resume_torrent(torrent_hash: str)`: Resume a torrent by its hash.

---

## 5. Radarr (`radarr_mcp.py`)
Movie management integration.
- **Environment Variables / Parameters:**
  - `RADARR_URL` (str): Radarr server URL.
  - `RADARR_API_KEY` (str): API Key.
- **Exposed Tools:**
  - `radarr_list_movies()`: List all movies managed in Radarr.
  - `radarr_search_movie(term: str)`: Search for a new movie to add in Radarr.
  - `radarr_get_movie_by_id(movie_id: int)`: Get detailed information for a specific Radarr movie ID.
  - `radarr_get_queue()`: Get current download queue in Radarr.
  - `radarr_list_commands()`: List running or completed commands in Radarr.

---

## 6. Seerr / Overseerr (`seerr_mcp.py`)
Media request management integration.
- **Environment Variables / Parameters:**
  - `SEERR_URL` (str): Seerr / Overseerr server URL.
  - `SEERR_API_KEY` (str): API Key.
- **Exposed Tools:**
  - `seerr_list_requests()`: List media requests in Seerr.
  - `seerr_search(query: str)`: Search movies or TV shows in Seerr.
  - `seerr_get_pending_requests()`: Get pending media requests awaiting approval.

---

## 7. Sonarr (`sonarr_mcp.py`)
TV series management integration.
- **Environment Variables / Parameters:**
  - `SONARR_URL` (str): Sonarr server URL.
  - `SONARR_API_KEY` (str): API Key.
- **Exposed Tools:**
  - `sonarr_list_series()`: List all TV series managed in Sonarr.
  - `sonarr_search_series(term: str)`: Search for a new TV series to add in Sonarr.
  - `sonarr_get_series_by_id(series_id: int)`: Get detailed information for a specific Sonarr series ID.
  - `sonarr_get_calendar(start_date: str = "", end_date: str = "")`: Get upcoming TV episodes calendar from Sonarr.
  - `sonarr_get_queue()`: Get current download queue in Sonarr.
  - `sonarr_list_commands()`: List running or completed commands in Sonarr.
