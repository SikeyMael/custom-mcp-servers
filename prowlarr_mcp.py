#!/usr/bin/env python3
"""Prowlarr MCP Server — full indexer, proxy, tag, download client, and search management."""

import os
import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("ProwlarrMCP")

PROWLARR_URL = os.environ.get("PROWLARR_URL", "http://localhost:9696")
PROWLARR_KEY = os.environ.get("PROWLARR_API_KEY", "")


def get_headers() -> dict:
    return {"X-Api-Key": PROWLARR_KEY}


def api_get(path: str, params: dict | None = None) -> dict | list:
    """GET request to Prowlarr API."""
    res = httpx.get(f"{PROWLARR_URL}{path}", headers=get_headers(), params=params, timeout=15)
    res.raise_for_status()
    return res.json()  # type: ignore[return-value]


def api_post(path: str, body: dict | None = None, params: dict | None = None) -> dict | list:
    """POST request to Prowlarr API."""
    res = httpx.post(
        f"{PROWLARR_URL}{path}",
        headers=get_headers(),
        json=body,
        params=params,
        timeout=15,
    )
    res.raise_for_status()
    if res.status_code == 204:
        return {"status": "no_content"}
    return res.json()  # type: ignore[return-value]


def api_put(path: str, body: dict | None = None, params: dict | None = None) -> dict | list:
    """PUT request to Prowlarr API."""
    res = httpx.put(
        f"{PROWLARR_URL}{path}",
        headers=get_headers(),
        json=body,
        params=params,
        timeout=15,
    )
    res.raise_for_status()
    if res.status_code == 204:
        return {"status": "no_content"}
    return res.json()  # type: ignore[return-value]


def api_delete(path: str) -> dict:
    """DELETE request to Prowlarr API."""
    res = httpx.delete(f"{PROWLARR_URL}{path}", headers=get_headers(), timeout=15)
    res.raise_for_status()
    return {"status": "deleted", "id": path.split("/")[-1]}


# ─── Indexer Management ───────────────────────────────────────────────

@mcp.tool()
def prowlarr_list_indexers() -> list:
    """List all configured indexers in Prowlarr."""
    return api_get("/api/v1/indexer")


@mcp.tool()
def prowlarr_get_indexer(indexer_id: int) -> dict:
    """Get a single indexer by ID."""
    return api_get(f"/api/v1/indexer/{indexer_id}")


@mcp.tool()
def prowlarr_create_indexer(
    name: str,
    implementation: str,
    config_contract: str,
    fields: list[dict] | None = None,
    app_profile_id: int | None = None,
    download_client_id: int | None = None,
    tags: list[int] | None = None,
    priority: int = 1,
    enable: bool = True,
) -> dict:
    """Create a new indexer.

    Args:
        name: Display name for the indexer.
        implementation: Implementation class name (e.g., 'Newznab', 'Torznab', 'Pneubot').
        config_contract: Configuration contract (e.g., 'NewznabSettings').
        fields: List of field dicts with 'name' and 'value' for this indexer type.
        app_profile_id: Application profile ID (e.g., 1 for default).
        download_client_id: Download client ID to assign.
        tags: List of tag IDs to apply.
        priority: Priority (1 = highest).
        enable: Whether the indexer is enabled.
    """
    body = {
        "name": name,
        "implementation": implementation,
        "configContract": config_contract,
        "fields": fields or [],
        "priority": priority,
        "enable": enable,
    }
    if app_profile_id is not None:
        body["appProfileId"] = app_profile_id
    if download_client_id is not None:
        body["downloadClientId"] = download_client_id
    if tags is not None:
        body["tags"] = tags
    return api_post("/api/v1/indexer", body=body)


@mcp.tool()
def prowlarr_update_indexer(
    indexer_id: int,
    name: str | None = None,
    fields: list[dict] | None = None,
    app_profile_id: int | None = None,
    download_client_id: int | None = None,
    tags: list[int] | None = None,
    priority: int | None = None,
    enable: bool | None = None,
) -> dict:
    """Update an existing indexer.

    Args:
        indexer_id: ID of the indexer to update.
        name: New display name.
        fields: Updated field dicts with 'name' and 'value'.
        app_profile_id: New application profile ID.
        download_client_id: New download client ID.
        tags: New list of tag IDs.
        priority: New priority (1 = highest).
        enable: New enabled state.
    """
    existing = prowlarr_get_indexer(indexer_id)
    if isinstance(existing, dict) and "error" in existing:
        return existing

    body = dict(existing)
    if name is not None:
        body["name"] = name
    if fields is not None:
        body["fields"] = fields
    if app_profile_id is not None:
        body["appProfileId"] = app_profile_id
    if download_client_id is not None:
        body["downloadClientId"] = download_client_id
    if tags is not None:
        body["tags"] = tags
    if priority is not None:
        body["priority"] = priority
    if enable is not None:
        body["enable"] = enable

    return api_put(f"/api/v1/indexer/{indexer_id}", body=body, params={"forceSave": True})


@mcp.tool()
def prowlarr_delete_indexer(indexer_id: int) -> dict:
    """Delete an indexer by ID."""
    return api_delete(f"/api/v1/indexer/{indexer_id}")


@mcp.tool()
def prowlarr_bulk_update_indexers(
    indexer_ids: list[int],
    tags: list[int] | None = None,
    enable: bool | None = None,
    app_profile_id: int | None = None,
    priority: int | None = None,
    minimum_seeders: int | None = None,
    seed_ratio: float | None = None,
    seed_time: int | None = None,
) -> dict:
    """Bulk update multiple indexers (tags, enable, priority, etc.).

    Args:
        indexer_ids: List of indexer IDs to update.
        tags: New tag IDs to apply.
        enable: Enable/disable all specified indexers.
        app_profile_id: New application profile ID.
        priority: New priority for all.
        minimum_seeders: Minimum seeders setting.
        seed_ratio: Seed ratio setting.
        seed_time: Seed time setting.
    """
    body: dict = {"ids": indexer_ids}
    if tags is not None:
        body["tags"] = tags
    if enable is not None:
        body["enable"] = enable
    if app_profile_id is not None:
        body["appProfileId"] = app_profile_id
    if priority is not None:
        body["priority"] = priority
    if minimum_seeders is not None:
        body["minimumSeeders"] = minimum_seeders
    if seed_ratio is not None:
        body["seedRatio"] = seed_ratio
    if seed_time is not None:
        body["seedTime"] = seed_time
    return api_put("/api/v1/indexer/bulk", body=body)


@mcp.tool()
def prowlarr_bulk_delete_indexers(indexer_ids: list[int]) -> dict:
    """Bulk delete multiple indexers by ID."""
    body = {"ids": indexer_ids}
    return api_delete("/api/v1/indexer/bulk")


@mcp.tool()
def prowlarr_get_indexer_schema(indexer_implementation: str | None = None) -> list:
    """Get the indexer schema for creating new indexers.

    Args:
        indexer_implementation: Optional filter by implementation name (e.g., 'Newznab', 'Torznab').
    """
    schema = api_get("/api/v1/indexer/schema")
    if indexer_implementation:
        schema = [i for i in schema if i.get("implementation") == indexer_implementation]
    return schema


@mcp.tool()
def prowlarr_test_indexer(indexer_id: int) -> dict:
    """Test a single indexer connection and configuration."""
    return api_post(f"/api/v1/indexer/test", params={"forceTest": True})


@mcp.tool()
def prowlarr_test_all_indexers() -> dict:
    """Test all configured indexers."""
    return api_post("/api/v1/indexer/testall")


@mcp.tool()
def prowlarr_run_indexer_action(
    action_name: str, indexer_ids: list[int] | None = None
) -> dict:
    """Run an action on indexer(s).

    Common action names: 'reindex', 'refresh', 'rss', 'deleteFailed'.

    Args:
        action_name: Action to run (e.g., 'reindex', 'refresh', 'rss').
        indexer_ids: Optional list of indexer IDs. If None, applies to all.
    """
    body = {}
    if indexer_ids:
        body["ids"] = indexer_ids
    return api_post(f"/api/v1/indexer/action/{action_name}", body=body)


# ─── Indexer Categories ───────────────────────────────────────────────

@mcp.tool()
def prowlarr_get_indexer_categories() -> list:
    """Get all available indexer categories and subcategories."""
    return api_get("/api/v1/indexer/categories")


# ─── Indexer Proxy Management ─────────────────────────────────────────

@mcp.tool()
def prowlarr_list_indexer_proxies() -> list:
    """List all configured indexer proxies."""
    return api_get("/api/v1/indexerproxy")


@mcp.tool()
def prowlarr_get_indexer_proxy(proxy_id: int) -> dict:
    """Get a single indexer proxy by ID."""
    return api_get(f"/api/v1/indexerproxy/{proxy_id}")


@mcp.tool()
def prowlarr_create_indexer_proxy(
    name: str,
    implementation: str,
    config_contract: str,
    fields: list[dict] | None = None,
    tags: list[int] | None = None,
) -> dict:
    """Create a new indexer proxy.

    Args:
        name: Display name for the proxy.
        implementation: Implementation class name.
        config_contract: Configuration contract.
        fields: Field dicts with 'name' and 'value'.
        tags: List of tag IDs.
    """
    body = {
        "name": name,
        "implementation": implementation,
        "configContract": config_contract,
        "fields": fields or [],
    }
    if tags is not None:
        body["tags"] = tags
    return api_post("/api/v1/indexerproxy", body=body)


@mcp.tool()
def prowlarr_update_indexer_proxy(
    proxy_id: int,
    name: str | None = None,
    fields: list[dict] | None = None,
    tags: list[int] | None = None,
) -> dict:
    """Update an existing indexer proxy."""
    existing = prowlarr_get_indexer_proxy(proxy_id)
    if isinstance(existing, dict) and "error" in existing:
        return existing

    body = dict(existing)
    if name is not None:
        body["name"] = name
    if fields is not None:
        body["fields"] = fields
    if tags is not None:
        body["tags"] = tags
    return api_put(f"/api/v1/indexerproxy/{proxy_id}", body=body, params={"forceSave": True})


@mcp.tool()
def prowlarr_delete_indexer_proxy(proxy_id: int) -> dict:
    """Delete an indexer proxy by ID."""
    return api_delete(f"/api/v1/indexerproxy/{proxy_id}")


@mcp.tool()
def prowlarr_get_indexer_proxy_schema() -> list:
    """Get the indexer proxy schema for creating new proxies."""
    return api_get("/api/v1/indexerproxy/schema")


@mcp.tool()
def prowlarr_test_indexer_proxy(proxy_id: int) -> dict:
    """Test a single indexer proxy."""
    return api_post(f"/api/v1/indexerproxy/test", params={"forceTest": True})


@mcp.tool()
def prowlarr_test_all_indexer_proxies() -> dict:
    """Test all indexer proxies."""
    return api_post("/api/v1/indexerproxy/testall")


# ─── Indexer Status & Statistics ──────────────────────────────────────

@mcp.tool()
def prowlarr_get_indexer_status() -> list:
    """Get the status of all indexers (disabledTill, failures, etc.)."""
    return api_get("/api/v1/indexerstatus")


@mcp.tool()
def prowlarr_get_indexer_stats() -> dict | list:
    """Get statistics for all indexers (response times, queries, grabs, failures).

    Returns the 'indexers' array from the stats endpoint.
    """
    data = api_get("/api/v1/indexerstats")
    if isinstance(data, dict) and "indexers" in data:
        return data["indexers"]
    return data  # type: ignore[return-value]


# ─── Tag Management ───────────────────────────────────────────────────

@mcp.tool()
def prowlarr_list_tags() -> list:
    """List all tags."""
    return api_get("/api/v1/tag")


@mcp.tool()
def prowlarr_create_tag(label: str, color: str | None = None, borderColor: str | None = None) -> dict:
    """Create a new tag.

    Args:
        label: Display label for the tag.
        color: Hex color code (e.g., '#ff0000').
        borderColor: Hex border color code.
    """
    body = {"label": label}
    if color:
        body["color"] = color
    if borderColor:
        body["borderColor"] = borderColor
    return api_post("/api/v1/tag", body=body)


@mcp.tool()
def prowlarr_delete_tag(tag_id: int) -> dict:
    """Delete a tag by ID."""
    return api_delete(f"/api/v1/tag/{tag_id}")


# ─── Download Client Management ───────────────────────────────────────

@mcp.tool()
def prowlarr_list_download_clients() -> list:
    """List all configured download clients."""
    return api_get("/api/v1/downloadclient")


@mcp.tool()
def prowlarr_get_download_client(client_id: int) -> dict:
    """Get a single download client by ID."""
    return api_get(f"/api/v1/downloadclient/{client_id}")


@mcp.tool()
def prowlarr_create_download_client(
    name: str,
    implementation: str,
    config_contract: str,
    fields: list[dict],
) -> dict:
    """Create a new download client.

    Args:
        name: Display name.
        implementation: Implementation class (e.g., 'qBittorrent', 'Deluge').
        config_contract: Configuration contract.
        fields: Field dicts with 'name' and 'value'.
    """
    body = {
        "name": name,
        "implementation": implementation,
        "configContract": config_contract,
        "fields": fields,
    }
    return api_post("/api/v1/downloadclient", body=body)


@mcp.tool()
def prowlarr_update_download_client(
    client_id: int,
    name: str | None = None,
    fields: list[dict] | None = None,
) -> dict:
    """Update an existing download client."""
    existing = prowlarr_get_download_client(client_id)
    if isinstance(existing, dict) and "error" in existing:
        return existing

    body = dict(existing)
    if name is not None:
        body["name"] = name
    if fields is not None:
        body["fields"] = fields
    return api_put(f"/api/v1/downloadclient/{client_id}", body=body, params={"forceSave": True})


@mcp.tool()
def prowlarr_delete_download_client(client_id: int) -> dict:
    """Delete a download client by ID."""
    return api_delete(f"/api/v1/downloadclient/{client_id}")


@mcp.tool()
def prowlarr_test_download_client(client_id: int) -> dict:
    """Test a download client connection."""
    return api_post(f"/api/v1/downloadclient/test", params={"forceTest": True})


@mcp.tool()
def prowlarr_get_download_client_schema() -> list:
    """Get the download client schema for creating new clients."""
    return api_get("/api/v1/downloadclient/schema")


# ─── Application Management ───────────────────────────────────────────

@mcp.tool()
def prowlarr_list_applications() -> list:
    """List connected applications (Sonarr, Radarr, etc.)."""
    return api_get("/api/v1/applications")


@mcp.tool()
def prowlarr_create_application(
    name: str,
    implementation: str,
    config_contract: str,
    fields: list[dict],
) -> dict:
    """Create a new application connection.

    Args:
        name: Display name (e.g., 'Sonarr').
        implementation: Implementation class.
        config_contract: Configuration contract.
        fields: Field dicts with 'name' and 'value'.
    """
    body = {
        "name": name,
        "implementation": implementation,
        "configContract": config_contract,
        "fields": fields,
    }
    return api_post("/api/v1/applications", body=body)


@mcp.tool()
def prowlarr_update_application(
    application_id: int,
    name: str | None = None,
    fields: list[dict] | None = None,
) -> dict:
    """Update an existing application connection."""
    existing = [a for a in prowlarr_list_applications() if a.get("id") == application_id]
    if not existing:
        return {"error": f"Application {application_id} not found"}
    body = dict(existing[0])
    if name is not None:
        body["name"] = name
    if fields is not None:
        body["fields"] = fields
    return api_put(f"/api/v1/applications/{application_id}", body=body, params={"forceSave": True})


@mcp.tool()
def prowlarr_delete_application(application_id: int) -> dict:
    """Delete an application connection by ID."""
    return api_delete(f"/api/v1/applications/{application_id}")


# ─── Search ───────────────────────────────────────────────────────────

@mcp.tool()
def prowlarr_search(
    term: str,
    indexer_ids: list[int] | None = None,
    category_id: int | None = None,
) -> list:
    """Search across indexers using Prowlarr's RSS/search endpoint.

    Args:
        term: Search query term.
        indexer_ids: Optional list of indexer IDs to search.
        category_id: Optional category ID to filter.
    """
    params = {"term": term}
    if indexer_ids:
        params["indexerIds"] = ",".join(str(i) for i in indexer_ids)
    if category_id is not None:
        params["categoryId"] = category_id
    return api_get("/api/v1/search", params=params)


# ─── Commands ─────────────────────────────────────────────────────────

@mcp.tool()
def prowlarr_list_commands() -> list:
    """List all running and completed commands."""
    return api_get("/api/v1/command")


@mcp.tool()
def prowlarr_run_command(
    name: str,
    indexer_id: int | None = None,
    download_client_id: int | None = None,
) -> dict:
    """Run a Prowlarr command (e.g., 'DownloadClientTestAll', 'IndexerTestAll', 'RefreshMonitoredDownloads').

    Args:
        name: Command name.
        indexer_id: Optional indexer ID for indexer-specific commands.
        download_client_id: Optional download client ID.
    """
    body = {"name": name}
    if indexer_id is not None:
        body["indexerId"] = indexer_id
    if download_client_id is not None:
        body["downloadClientId"] = download_client_id
    return api_post("/api/v1/command", body=body)


@mcp.tool()
def prowlarr_get_command(command_id: int) -> dict:
    """Get a command by ID (check progress/status)."""
    return api_get(f"/api/v1/command/{command_id}")


# ─── System ───────────────────────────────────────────────────────────

@mcp.tool()
def prowlarr_get_api_info() -> dict:
    """Get Prowlarr API info and version."""
    return api_get("/api")


@mcp.tool()
def prowlarr_get_health() -> list:
    """Check Prowlarr health (warnings, errors)."""
    return api_get("/api/v1/health")


@mcp.tool()
def prowlarr_shutdown() -> dict:
    """Shut down Prowlarr."""
    return api_post("/api/v1/system/shutdown")


@mcp.tool()
def prowlarr_restart() -> dict:
    """Restart Prowlarr."""
    return api_post("/api/v1/system/restart")


if __name__ == "__main__":
    mcp.run()
