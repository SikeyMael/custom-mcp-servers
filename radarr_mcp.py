#!/usr/bin/env python3
"""Radarr MCP Server — full v3 API coverage for movie management, release selection, and download control."""
import os
import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("RadarrMCP")

RADARR_URL = os.environ.get("RADARR_URL", "http://localhost:7878")
RADARR_KEY = os.environ.get("RADARR_API_KEY", "")


def get_headers():
    return {"X-Api-Key": RADARR_KEY}


def api_get(path: str, params: dict | None = None) -> dict | list:
    """GET request to Radarr API."""
    res = httpx.get(f"{RADARR_URL}{path}", headers=get_headers(), params=params, timeout=30)
    res.raise_for_status()
    return res.json()


def api_post(path: str, data: dict | None = None) -> dict | list:
    """POST request to Radarr API."""
    res = httpx.post(f"{RADARR_URL}{path}", json=data, headers=get_headers(), timeout=30)
    res.raise_for_status()
    if res.status_code == 204:
        return {}
    return res.json()


def api_put(path: str, data: dict) -> dict | list:
    """PUT request to Radarr API."""
    res = httpx.put(f"{RADARR_URL}{path}", json=data, headers=get_headers(), timeout=30)
    res.raise_for_status()
    if res.status_code == 204:
        return {}
    return res.json()


def api_delete(path: str) -> dict | list:
    """DELETE request to Radarr API."""
    res = httpx.delete(f"{RADARR_URL}{path}", headers=get_headers(), timeout=30)
    if res.status_code in (200, 204):
        return {"status": "deleted"}
    return res.json()


# ──────────────────────────────────────────────
# MOVIE MANAGEMENT
# ──────────────────────────────────────────────

@mcp.tool()
def radarr_list_movies(include_images: bool = True) -> list:
    """List all movies managed in Radarr."""
    return api_get("/api/v3/movie", {"includeImages": include_images})


@mcp.tool()
def radarr_get_movie_by_id(movie_id: int, include_images: bool = True) -> dict:
    """Get detailed information for a specific Radarr movie by ID."""
    return api_get(f"/api/v3/movie/{movie_id}", {"includeImages": include_images})


@mcp.tool()
def radarr_add_movie(
    title: str,
    tmdb_id: int,
    root_path: str,
    quality_profile_id: int = 1,
    language_profile_id: int = 1,
    monited: bool = True,
    search_for_movie: bool = False,
    minimum_availability: str = "TBD",
    title_cutoff: int = 0,
    tags: list | None = None,
    quality_profile_name: str = "",
    movie_folder: str = "",
) -> dict:
    """Add a new movie to Radarr. Requires tmdb_id and root_path. Sets search_for_movie=True to trigger immediate search."""
    movie = {
        "title": title,
        "tmdbId": tmdb_id,
        "rootFolderPath": root_path,
        "qualityProfileId": quality_profile_id,
        "languageProfileId": language_profile_id,
        "monitored": monited,
        "searchForMovie": search_for_movie,
        "minimumAvailability": minimum_availability,
        "titleCutoffId": title_cutoff,
        "tags": tags or [],
    }
    if quality_profile_name:
        profiles = api_get("/api/v3/qualityprofile")
        for p in profiles:
            if p["name"] == quality_profile_name:
                movie["qualityProfileId"] = p["id"]
                break
    if movie_folder:
        movie["movieFolder"] = movie_folder
    return api_post("/api/v3/movie", movie)


@mcp.tool()
def radarr_update_movie(movie_id: int, **kwargs) -> dict | list:
    """Update an existing movie in Radarr. Pass any movie fields as kwargs (title, monitored, qualityProfileId, tags, etc.)."""
    existing = api_get(f"/api/v3/movie/{movie_id}")
    if isinstance(existing, dict):
        existing.update(kwargs)
        return api_put(f"/api/v3/movie/{movie_id}", existing)
    return {"error": "Expected dict response"}


@mcp.tool()
def radarr_delete_movie(movie_id: int, delete_files: bool = False) -> dict | list:
    """Delete a movie from Radarr. Set delete_files=True to remove files from disk."""
    return api_delete(f"/api/v3/movie/{movie_id}?deleteFiles={delete_files}")


@mcp.tool()
def radarr_get_movie_files(movie_id: int) -> list:
    """List all movie files (downloaded releases) for a specific movie."""
    return api_get(f"/api/v3/moviefile", {"movieId": movie_id})


@mcp.tool()
def radarr_delete_movie_file(file_id: int) -> dict | list:
    """Delete a specific movie file from Radarr's library."""
    return api_delete(f"/api/v3/moviefile/{file_id}")


# ──────────────────────────────────────────────
# MOVIE LOOKUP / SEARCH
# ──────────────────────────────────────────────

@mcp.tool()
def radarr_lookup_movie_tmdb(query: str) -> list:
    """Search movies by TMDB title. Returns list of matching movies with tmdbId, title, year, images."""
    return api_get("/api/v3/movie/lookup/tmdb", {"term": query})


@mcp.tool()
def radarr_lookup_movie_imdb(query: str) -> list:
    """Search movies by IMDB title. Returns list of matching movies with imdbId, title, year."""
    return api_get("/api/v3/movie/lookup/imdb", {"term": query})


@mcp.tool()
def radarr_lookup_movie(term: str) -> list:
    """Generic movie lookup across all sources (TMDB, IMDB). Returns list of matching movies."""
    return api_get("/api/v3/movie/lookup", {"term": term})


@mcp.tool()
def radarr_parse_title(text: str) -> dict:
    """Parse a movie title from free text (e.g. from a torrent name). Returns title, year, and quality info."""
    return api_get("/api/v3/parse", {"term": text})


# ──────────────────────────────────────────────
# RELEASE MANAGEMENT (CRITICAL for selection)
# ──────────────────────────────────────────────

@mcp.tool()
def radarr_get_releases(movie_id: int, indexer_id: int | None = None) -> list:
    """Get all available releases for a movie. Optionally filter by indexer_id. Shows quality, size, protocol, age, download_count."""
    params = {"movieId": movie_id}
    if indexer_id is not None:
        params["indexerId"] = indexer_id
    return api_get("/api/v3/release", params)


@mcp.tool()
def radarr_force_grab_release(
    release_id: int,
    download_client_id: int | None = None,
) -> dict:
    """Force grab (download) a specific release by release_id. Optionally specify download_client_id."""
    data = {"releaseId": release_id}
    if download_client_id is not None:
        data["downloadClientId"] = download_client_id
    return api_post("/api/v3/release", data)


# ──────────────────────────────────────────────
# QUEUE MANAGEMENT
# ──────────────────────────────────────────────

@mcp.tool()
def radarr_get_queue(page: int = 1, page_size: int = 50, include_movie: bool = True) -> dict:
    """Get current download queue with pagination. include_movie=True adds movie details to each entry."""
    return api_get("/api/v3/queue", {
        "page": page,
        "pageSize": page_size,
        "includeMovie": include_movie,
    })


@mcp.tool()
def radarr_get_queue_details(movie_id: int) -> list:
    """Get queue entries filtered by a specific movie ID."""
    return api_get("/api/v3/queue/details", {"movieId": movie_id})


@mcp.tool()
def radarr_remove_from_queue(item_id: int, blocklist: bool = False) -> dict | list:
    """Remove a single item from the download queue. blocklist=True adds it to the blocklist."""
    return api_delete(f"/api/v3/queue/{item_id}?blocklist={blocklist}")


@mcp.tool()
def radarr_bulk_remove_from_queue(ids: list, blocklist: bool = False) -> dict | list:
    """Remove multiple items from the download queue at once."""
    return api_delete(f"/api/v3/queue/bulk?blocklist={blocklist}", )


@mcp.tool()
def radarr_grab_release(item_id: int) -> dict | list:
    """Manually grab a queued release (mark as downloaded). Used for manual import workflows."""
    return api_post(f"/api/v3/queue/grab/{item_id}", {})


@mcp.tool()
def radarr_get_queue_status() -> dict:
    """Get overall queue status (total items, size, bandwidth)."""
    return api_get("/api/v3/queue/status")


# ──────────────────────────────────────────────
# MANUAL IMPORT
# ──────────────────────────────────────────────

@mcp.tool()
def radarr_list_manual_import_files(folder_path: str) -> list:
    """List media files in a folder for manual import. Useful when files are already downloaded outside Radarr."""
    return api_get("/api/v3/manualimport", {"path": folder_path})


@mcp.tool()
def radarr_manual_import(files: list) -> list:
    """Import files manually into Radarr. Pass list of dicts with: movieId, folderPath, quality, name, size, releaseTitle, indexerFlags."""
    return api_post("/api/v3/manualimport", {"files": files})


@mcp.tool()
def radarr_import_existing_movie(
    movie_id: int,
    folder_path: str,
    download_client_id: int | None = None,
) -> dict:
    """Import an already-downloaded movie folder into Radarr's library."""
    data = {"movieId": movie_id, "folderPath": folder_path}
    if download_client_id is not None:
        data["downloadClientId"] = download_client_id
    return api_post("/api/v3/movie/import", data)


# ──────────────────────────────────────────────
# WANTED / MISSING
# ──────────────────────────────────────────────

@mcp.tool()
def radarr_get_missing_movies(page: int = 1, page_size: int = 50) -> dict:
    """Get all movies that are missing (no release available yet). Paginated."""
    return api_get("/api/v3/wanted/missing", {"page": page, "pageSize": page_size})


@mcp.tool()
def radarr_get_cutoff_unmet(page: int = 1, page_size: int = 50) -> dict:
    """Get movies with unmet cutoff requirements (better quality available but not yet downloaded). Paginated."""
    return api_get("/api/v3/wanted/cutoff", {"page": page, "pageSize": page_size})


# ──────────────────────────────────────────────
# HISTORY
# ──────────────────────────────────────────────

@mcp.tool()
def radarr_get_history(movie_id: int | None = None, page: int = 1, page_size: int = 50) -> dict:
    """Get download history. Optional movie_id to filter by specific movie."""
    params = {"page": page, "pageSize": page_size}
    if movie_id is not None:
        params["movieId"] = movie_id
    return api_get("/api/v3/history", params)


@mcp.tool()
def radarr_get_history_since(hours: int = 24) -> list:
    """Get download history since a given number of hours ago."""
    return api_get(f"/api/v3/history/since?hours={hours}")


@mcp.tool()
def radarr_mark_as_failed(history_id: int) -> dict | list:
    """Mark a history entry as failed (re-queue for re-download)."""
    return api_post(f"/api/v3/history/failed/{history_id}", {})


# ──────────────────────────────────────────────
# BLOCKLIST
# ──────────────────────────────────────────────

@mcp.tool()
def radarr_get_blocklist(movie_id: int | None = None, page: int = 1, page_size: int = 50) -> dict:
    """Get the blocklist (blocked releases). Optional movie_id filter."""
    params = {"page": page, "pageSize": page_size}
    if movie_id is not None:
        params["movieId"] = movie_id
    return api_get("/api/v3/blocklist", params)


@mcp.tool()
def radarr_remove_from_blocklist(blocklist_id: int) -> dict | list:
    """Remove an item from the blocklist (unblock a release)."""
    return api_delete(f"/api/v3/blocklist/{blocklist_id}")


# ──────────────────────────────────────────────
# CONFIGURATION & RESOURCES
# ──────────────────────────────────────────────

@mcp.tool()
def radarr_get_quality_profiles() -> list:
    """List all available quality profiles (defines which qualities Radarr will accept)."""
    return api_get("/api/v3/qualityprofile")


@mcp.tool()
def radarr_get_indexers() -> list:
    """List all configured indexers (torrent/newsgroup sources for finding releases)."""
    return api_get("/api/v3/indexer")


@mcp.tool()
def radarr_get_download_clients() -> list:
    """List all configured download clients (qBittorrent, SABnzbd, etc.)."""
    return api_get("/api/v3/downloadclient")


@mcp.tool()
def radarr_get_root_folders() -> list:
    """List all configured root folders on disk where movies are stored."""
    return api_get("/api/v3/rootfolder")


@mcp.tool()
def radarr_get_tags() -> list:
    """List all available tags for organizing movies."""
    return api_get("/api/v3/tag")


@mcp.tool()
def radarr_get_languages() -> list:
    """List all available audio languages."""
    return api_get("/api/v3/language")


@mcp.tool()
def radarr_get_remote_path_mappings() -> list:
    """List remote path mappings (for download client ↔ Radarr path translation)."""
    return api_get("/api/v3/remotepathmapping")


# ──────────────────────────────────────────────
# COMMANDS / ACTIONS
# ──────────────────────────────────────────────

@mcp.tool()
def radarr_run_command(
    name: str,
    movie_id: int | None = None,
) -> dict | list:
    """Run a Radarr system command. Common names: 'backfill', 'refreshmonitoredmovies', 'moviesearch', 'rescan'. For moviesearch, pass movie_id."""
    data = {"name": name}
    if movie_id is not None:
        data["movieId"] = movie_id
    return api_post("/api/v3/command", data)


@mcp.tool()
def radarr_list_commands() -> list:
    """List all running and completed commands in Radarr."""
    return api_get("/api/v3/command")


@mcp.tool()
def radarr_get_command_status(command_id: int) -> dict | list:
    """Get status of a specific command by ID (progress, error message)."""
    return api_get(f"/api/v3/command/{command_id}")


# ──────────────────────────────────────────────
# SYSTEM INFO
# ──────────────────────────────────────────────

@mcp.tool()
def radarr_get_system_status() -> dict:
    """Get Radarr system status (instance name, version, url, stopTime)."""
    return api_get("/api/v3/system/status")


@mcp.tool()
def radarr_get_disk_space() -> list:
    """Get disk space information for all configured folders."""
    return api_get("/api/v3/diskspace")


if __name__ == "__main__":
    mcp.run()
