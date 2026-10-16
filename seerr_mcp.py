#!/usr/bin/env python3
"""Seerr / Overseerr MCP Server — full coverage of the most important API endpoints.

Environment variables:
  SEERR_URL     — base URL (e.g. http://localhost:5055)
  SEERR_API_KEY — API key generated in Seerr settings

Endpoints implemented:
  Search & Discovery: search, discover_movies, discover_tv, trending, upcoming, genres
  Details: movie_details, tv_details, tv_season, recommendations, similar, ratings, person, collection
  Requests: request_movie, request_tv, update_request, delete_request, retry_request,
            get_request, list_requests, pending_requests, request_count, user_requests
  Media: list_media, delete_media, update_media_status
  Users: get_user, list_users
  Issues: list_issues, create_issue
  Watchlist: add_watchlist, remove_watchlist
  Services: radarr_servers, sonarr_servers, radarr_server_info, sonarr_server_info
  Blocklist: list_blocklist, add_blocklist, remove_blocklist
  Misc: status, regions, languages, backdrops
"""

import os
import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("SeerrMCP")

SEERR_URL = os.environ.get("SEERR_URL", "http://localhost:5055")
SEERR_KEY = os.environ.get("SEERR_API_KEY", "")


def _params(extra: dict | None = None) -> dict:
    """Build query params dict with API key."""
    q = {"apikey": SEERR_KEY}
    if extra:
        q.update(extra)
    return q


def _headers():
    return {"X-Api-Key": SEERR_KEY}


def get(path: str, params: dict | None = None) -> dict | list:
    """GET request to /api/v1/<path>."""
    q = _params(params)
    res = httpx.get(f"{SEERR_URL}/api/v1{path}", params=q, headers=_headers(), timeout=15)
    res.raise_for_status()
    return res.json()


def post(path: str, json_body: dict | None = None) -> dict:
    """POST request to /api/v1/<path>."""
    q = _params()
    res = httpx.post(f"{SEERR_URL}/api/v1{path}", params=q, json=json_body, headers=_headers(), timeout=15)
    if res.status_code == 204:
        return {}
    res.raise_for_status()
    return res.json()


def put(path: str, json_body: dict | None = None) -> dict:
    """PUT request to /api/v1/<path>."""
    q = _params()
    res = httpx.put(f"{SEERR_URL}/api/v1{path}", params=q, json=json_body, headers=_headers(), timeout=15)
    if res.status_code == 204:
        return {}
    res.raise_for_status()
    return res.json()


def delete(path: str) -> dict:
    """DELETE request to /api/v1/<path>."""
    q = _params()
    res = httpx.delete(f"{SEERR_URL}/api/v1{path}", params=q, headers=_headers(), timeout=15)
    if res.status_code == 204:
        return {}
    res.raise_for_status()
    return res.json()


# ─── Status & Misc ───────────────────────────────────────────────────────────

@mcp.tool()
def seerr_status() -> dict:
    """Get Seerr server status and uptime."""
    return get("/status")


@mcp.tool()
def seerr_regions() -> list:
    """Get list of regions supported by TMDB for content filtering."""
    return get("/regions")


@mcp.tool()
def seerr_languages() -> list:
    """Get list of languages supported by TMDB."""
    return get("/languages")


@mcp.tool()
def seerr_backdrops(page: int = 1) -> list:
    """Get backdrop images of trending items."""
    return get("/backdrops", {"page": page})


# ─── Search & Discovery ──────────────────────────────────────────────────────

@mcp.tool()
def seerr_search(query: str, page: int = 1, language: str = "en") -> dict:
    """Search for movies, TV shows, or people by name.

    Args:
        query: Search term (e.g. 'The Matrix')
        page: Page number for pagination (default 1)
        language: Language code for results (default 'en')
    """
    return get("/search", {"query": query, "page": page, "language": language})


@mcp.tool()
def seerr_search_keyword(keyword: str, page: int = 1) -> dict:
    """Search for TMDB keywords by name.

    Args:
        keyword: Keyword to search for
        page: Page number (default 1)
    """
    return get("/search/keyword", {"query": keyword, "page": page})


@mcp.tool()
def seerr_search_company(company: str, page: int = 1) -> dict:
    """Search for production companies by name.

    Args:
        company: Company name to search for
        page: Page number (default 1)
    """
    return get("/search/company", {"query": company, "page": page})


@mcp.tool()
def seerr_discover_movies(
    page: int = 1,
    genre: int | None = None,
    studio: int | None = None,
    keywords: str | None = None,
    sort_by: str = "popularity.desc",
    release_date_gte: str | None = None,
    release_date_lte: str | None = None,
    vote_average_gte: float | None = None,
    vote_count_gte: int | None = None,
    watch_region: str | None = None,
    language: str = "en",
) -> dict:
    """Discover movies by various filters (genre, studio, date range, rating, etc.).

    Args:
        page: Page number (default 1)
        genre: TMDB genre ID (e.g. 28 for Action, 35 for Comedy)
        studio: TMDB studio ID
        keywords: Comma-separated keyword IDs to include
        sort_by: Sort field (default 'popularity.desc'). Examples: 'release_date.desc', 'vote_average.desc'
        release_date_gte: Start date filter (e.g. '2022-01-01')
        release_date_lte: End date filter (e.g. '2024-12-31')
        vote_average_gte: Minimum average vote (e.g. 7.0)
        vote_count_gte: Minimum vote count (e.g. 100)
        watch_region: Two-letter country code for streaming availability (e.g. 'US', 'IT')
        language: Language code for results (default 'en')
    """
    params = {"page": page, "language": language, "sortBy": sort_by}
    if genre:
        params["genre"] = str(genre)
    if studio:
        params["studio"] = str(studio)
    if keywords:
        params["keywords"] = keywords
    if release_date_gte:
        params["primaryReleaseDateGte"] = release_date_gte
    if release_date_lte:
        params["primaryReleaseDateLte"] = release_date_lte
    if vote_average_gte is not None:
        params["voteAverageGte"] = str(vote_average_gte)
    if vote_count_gte is not None:
        params["voteCountGte"] = str(vote_count_gte)
    if watch_region:
        params["watchRegion"] = watch_region
    return get("/discover/movies", params)


@mcp.tool()
def seerr_discover_tv(
    page: int = 1,
    genre: int | None = None,
    network: int | None = None,
    sort_by: str = "popularity.desc",
    first_air_date_gte: str | None = None,
    vote_average_gte: float | None = None,
    watch_region: str | None = None,
    language: str = "en",
) -> dict:
    """Discover TV shows by various filters (genre, network, date range, rating, etc.).

    Args:
        page: Page number (default 1)
        genre: TMDB genre ID (e.g. 18 for Drama, 10765 for Sci-Fi)
        network: TMDB network ID (e.g. 213 for Netflix)
        sort_by: Sort field (default 'popularity.desc')
        first_air_date_gte: Start date filter (e.g. '2022-01-01')
        vote_average_gte: Minimum average vote (e.g. 7.0)
        watch_region: Two-letter country code for streaming availability
        language: Language code for results (default 'en')
    """
    params = {"page": page, "language": language, "sortBy": sort_by}
    if genre:
        params["genre"] = str(genre)
    if network:
        params["network"] = str(network)
    if first_air_date_gte:
        params["firstAirDateGte"] = first_air_date_gte
    if vote_average_gte is not None:
        params["voteAverageGte"] = str(vote_average_gte)
    if watch_region:
        params["watchRegion"] = watch_region
    return get("/discover/tv", params)


@mcp.tool()
def seerr_trending(time_window: str = "week", media_type: str = "all", page: int = 1, language: str = "en") -> dict:
    """Get trending movies and TV shows.

    Args:
        time_window: 'day' or 'week' (default 'week')
        media_type: 'movie', 'tv', or 'all' (default 'all')
        page: Page number (default 1)
        language: Language code (default 'en')
    """
    return get("/discover/trending", {"timeWindow": time_window, "mediaType": media_type, "page": page, "language": language})


@mcp.tool()
def seerr_upcoming_movies(page: int = 1, region: str | None = None, language: str = "en") -> dict:
    """Get upcoming movies by release date.

    Args:
        page: Page number (default 1)
        region: Region code for release dates (e.g. 'US', 'IT')
        language: Language code (default 'en')
    """
    params = {"page": page, "language": language}
    if region:
        params["region"] = region
    return get("/discover/movies/upcoming", params)


@mcp.tool()
def seerr_upcoming_tv(page: int = 1, language: str = "en") -> dict:
    """Get upcoming TV shows by air date.

    Args:
        page: Page number (default 1)
        language: Language code (default 'en')
    """
    return get("/discover/tv/upcoming", {"page": page, "language": language})


@mcp.tool()
def seerr_movie_genres() -> list:
    """Get the list of official TMDB movie genre IDs and names."""
    return get("/genres/movie")


@mcp.tool()
def seerr_tv_genres() -> list:
    """Get the list of official TMDB TV genre IDs and names."""
    return get("/genres/tv")


# ─── Details ─────────────────────────────────────────────────────────────────

@mcp.tool()
def seerr_movie_details(movie_id: int, language: str = "en") -> dict:
    """Get detailed information about a movie by TMDB ID.

    Args:
        movie_id: TMDB movie ID
        language: Language code for results (default 'en')
    """
    return get(f"/movie/{movie_id}", {"language": language})


@mcp.tool()
def seerr_tv_details(tv_id: int, language: str = "en") -> dict:
    """Get detailed information about a TV show by TMDB ID.

    Args:
        tv_id: TMDB TV show ID
        language: Language code for results (default 'en')
    """
    return get(f"/tv/{tv_id}", {"language": language})


@mcp.tool()
def seerr_tv_season(tv_id: int, season_number: int, language: str = "en") -> dict:
    """Get season details and episode list for a TV show.

    Args:
        tv_id: TMDB TV show ID
        season_number: Season number (0 for specials)
        language: Language code (default 'en')
    """
    return get(f"/tv/{tv_id}/season/{season_number}", {"language": language})


@mcp.tool()
def seerr_movie_recommendations(movie_id: int, page: int = 1, language: str = "en") -> dict:
    """Get recommended movies similar to the given movie.

    Args:
        movie_id: TMDB movie ID
        page: Page number (default 1)
        language: Language code (default 'en')
    """
    return get(f"/movie/{movie_id}/recommendations", {"page": page, "language": language})


@mcp.tool()
def seerr_movie_similar(movie_id: int, page: int = 1, language: str = "en") -> dict:
    """Get movies similar to the given movie.

    Args:
        movie_id: TMDB movie ID
        page: Page number (default 1)
        language: Language code (default 'en')
    """
    return get(f"/movie/{movie_id}/similar", {"page": page, "language": language})


@mcp.tool()
def seerr_tv_similar(tv_id: int, page: int = 1, language: str = "en") -> dict:
    """Get TV shows similar to the given TV show.

    Args:
        tv_id: TMDB TV show ID
        page: Page number (default 1)
        language: Language code (default 'en')
    """
    return get(f"/tv/{tv_id}/similar", {"page": page, "language": language})


@mcp.tool()
def seerr_tv_recommendations(tv_id: int, page: int = 1, language: str = "en") -> dict:
    """Get recommended TV shows similar to the given TV show.

    Args:
        tv_id: TMDB TV show ID
        page: Page number (default 1)
        language: Language code (default 'en')
    """
    return get(f"/tv/{tv_id}/recommendations", {"page": page, "language": language})


@mcp.tool()
def seerr_movie_ratings(movie_id: int, language: str = "en") -> dict:
    """Get movie ratings from TMDB, Rotten Tomatoes, and IMDb.

    Args:
        movie_id: TMDB movie ID
        language: Language code (default 'en')
    """
    return get(f"/movie/{movie_id}/ratings", {"language": language})


@mcp.tool()
def seerr_tv_ratings(tv_id: int, language: str = "en") -> dict:
    """Get TV show ratings from TMDB, Rotten Tomatoes, and IMDb.

    Args:
        tv_id: TMDB TV show ID
        language: Language code (default 'en')
    """
    return get(f"/tv/{tv_id}/ratings", {"language": language})


@mcp.tool()
def seerr_person_details(person_id: int, language: str = "en") -> dict:
    """Get details about a person (actor, director, etc.) by TMDB ID.

    Args:
        person_id: TMDB person ID
        language: Language code (default 'en')
    """
    return get(f"/person/{person_id}", {"language": language})


@mcp.tool()
def seerr_person_combined_credits(person_id: int, language: str = "en") -> dict:
    """Get combined credits (acting + crew) for a person.

    Args:
        person_id: TMDB person ID
        language: Language code (default 'en')
    """
    return get(f"/person/{person_id}/combined_credits", {"language": language})


@mcp.tool()
def seerr_collection_details(collection_id: int, language: str = "en") -> dict:
    """Get details about a movie collection by TMDB ID.

    Args:
        collection_id: TMDB collection ID
        language: Language code (default 'en')
    """
    return get(f"/collection/{collection_id}", {"language": language})


@mcp.tool()
def seerr_studio_details(studio_id: int) -> dict:
    """Get details about a movie studio by TMDB ID.

    Args:
        studio_id: TMDB studio ID
    """
    return get(f"/studio/{studio_id}")


@mcp.tool()
def seerr_network_details(network_id: int) -> dict:
    """Get details about a TV network by TMDB ID.

    Args:
        network_id: TMDB network ID
    """
    return get(f"/network/{network_id}")


# ─── Requests ────────────────────────────────────────────────────────────────

@mcp.tool()
def seerr_request_movie(
    tmdb_id: int,
    media_language_profile_id: int | None = None,
    quality_profile_id: int | None = None,
    server_id: int | None = None,
    profile_id: int | None = None,
    is_4k: bool = False,
    ignore_quota: bool = False,
) -> dict:
    """Request a movie by TMDB ID.

    Args:
        tmdb_id: TMDB movie ID
        media_language_profile_id: Language profile ID (for dubbing/subtitle preferences)
        quality_profile_id: Quality profile ID for the media server
        server_id: Media server ID (Radarr/Sonarr instance)
        profile_id: User profile ID to associate with the request
        is_4k: Whether this is a 4K request (default False)
        ignore_quota: Skip quota checks (requires MANAGE_REQUESTS permission)
    """
    body = {
        "mediaType": "movie",
        "mediaId": tmdb_id,
        "is4k": is_4k,
    }
    if media_language_profile_id is not None:
        body["languageProfileId"] = media_language_profile_id
    if quality_profile_id is not None:
        body["qualityProfileId"] = quality_profile_id
    if server_id is not None:
        body["serverId"] = server_id
    if profile_id is not None:
        body["profileId"] = profile_id
    if ignore_quota:
        body["ignoreQuota"] = True
    return post("/request", body)


@mcp.tool()
def seerr_request_tv(
    tmdb_id: int,
    seasons: int | str | list[int] | None = None,
    media_language_profile_id: int | None = None,
    quality_profile_id: int | None = None,
    server_id: int | None = None,
    profile_id: int | None = None,
    is_4k: bool = False,
    ignore_quota: bool = False,
) -> dict:
    """Request a TV show by TMDB ID.

    Args:
        tmdb_id: TMDB TV show ID
        seasons: Which seasons to request. Options:
            - 'all' or 0: all seasons
            - int: single season number
            - list[int]: specific seasons, e.g. [1, 2, 3]
            - None: default (all available)
        media_language_profile_id: Language profile ID
        quality_profile_id: Quality profile ID
        server_id: Media server ID
        profile_id: User profile ID
        is_4k: Whether this is a 4K request (default False)
        ignore_quota: Skip quota checks (requires MANAGE_REQUESTS permission)
    """
    body = {
        "mediaType": "tv",
        "mediaId": tmdb_id,
        "is4k": is_4k,
    }
    if seasons is not None:
        body["seasons"] = seasons
    if media_language_profile_id is not None:
        body["languageProfileId"] = media_language_profile_id
    if quality_profile_id is not None:
        body["qualityProfileId"] = quality_profile_id
    if server_id is not None:
        body["serverId"] = server_id
    if profile_id is not None:
        body["profileId"] = profile_id
    if ignore_quota:
        body["ignoreQuota"] = True
    return post("/request", body)


@mcp.tool()
def seerr_get_request(request_id: int) -> dict:
    """Get details of a specific request by ID.

    Args:
        request_id: Seerr request ID
    """
    return get(f"/request/{request_id}")


@mcp.tool()
def seerr_update_request(
    request_id: int,
    status: str | None = None,
    media_language_profile_id: int | None = None,
    quality_profile_id: int | None = None,
    server_id: int | None = None,
    profile_id: int | None = None,
    is_4k: bool | None = None,
) -> dict:
    """Update an existing request (status, server, profile, etc.).

    Args:
        request_id: Seerr request ID
        status: New status ('approved', 'failed', 'cancelled', etc.)
        media_language_profile_id: Language profile ID
        quality_profile_id: Quality profile ID
        server_id: Media server ID
        profile_id: User profile ID
        is_4k: Toggle 4K flag
    """
    body = {}
    if status is not None:
        body["status"] = status
    if media_language_profile_id is not None:
        body["languageProfileId"] = media_language_profile_id
    if quality_profile_id is not None:
        body["qualityProfileId"] = quality_profile_id
    if server_id is not None:
        body["serverId"] = server_id
    if profile_id is not None:
        body["profileId"] = profile_id
    if is_4k is not None:
        body["is4k"] = is_4k
    return put(f"/request/{request_id}", body)


@mcp.tool()
def seerr_delete_request(request_id: int) -> dict:
    """Delete a request by ID.

    Args:
        request_id: Seerr request ID
    """
    return delete(f"/request/{request_id}")


@mcp.tool()
def seerr_retry_request(request_id: int) -> dict:
    """Retry a failed request (re-check availability).

    Args:
        request_id: Seerr request ID
    """
    return post(f"/request/{request_id}/retry")


@mcp.tool()
def seerr_list_requests(
    filter: str | None = None,
    sort_by: str = "createdAt",
    sort_order: str = "desc",
    page: int = 1,
    take: int = 20,
) -> dict:
    """List all media requests with optional filtering and pagination.

    Args:
        filter: Filter by status: 'all', 'available', 'partial', 'processing', 'pending', 'failed', 'cancelled', 'deleted'
        sort_by: Sort field (default 'createdAt')
        sort_order: 'asc' or 'desc' (default 'desc')
        page: Page number (default 1)
        take: Items per page (default 20)
    """
    params = {"sortBy": sort_by, "sortOrder": sort_order, "page": page, "take": take}
    if filter:
        params["filter"] = filter
    return get("/request", params)


@mcp.tool()
def seerr_get_pending_requests() -> dict:
    """Get pending media requests awaiting approval."""
    return get("/request", {"filter": "pending"})


@mcp.tool()
def seerr_request_count() -> dict:
    """Get request counts broken down by status and media type."""
    return get("/request/count")


@mcp.tool()
def seerr_user_requests(user_id: int, filter: str | None = None) -> dict:
    """Get requests made by a specific user.

    Args:
        user_id: User ID in Seerr
        filter: Optional status filter
    """
    params = {}
    if filter:
        params["filter"] = filter
    return get(f"/user/{user_id}/requests", params)


# ─── Media ───────────────────────────────────────────────────────────────────

@mcp.tool()
def seerr_list_media(
    take: int = 20,
    skip: int = 0,
    filter: str | None = None,
    sort: str = "added",
) -> dict:
    """List media items that have been processed/downloaded in Seerr.

    Args:
        take: Items per page (default 20)
        skip: Items to skip for pagination (default 0)
        filter: Filter by status: 'all', 'available', 'partial', 'allavailable', 'processing', 'pending', 'deleted'
        sort: Sort by 'added', 'modified', or 'mediaAdded' (default 'added')
    """
    params = {"take": take, "skip": skip, "sort": sort}
    if filter:
        params["filter"] = filter
    return get("/media", params)


@mcp.tool()
def seerr_delete_media(media_id: int) -> dict:
    """Delete a media item from Seerr.

    Args:
        media_id: Seerr media ID
    """
    return delete(f"/media/{media_id}")


@mcp.tool()
def seerr_update_media_status(media_id: int, status: str) -> dict:
    """Update the processing status of a media item.

    Args:
        media_id: Seerr media ID
        status: New status ('available', 'processing', 'missing', etc.)
    """
    return post(f"/media/{media_id}/{status}")


# ─── Users ───────────────────────────────────────────────────────────────────

@mcp.tool()
def seerr_list_users() -> list:
    """Get all Seerr users."""
    return get("/user")


@mcp.tool()
def seerr_get_user(user_id: int) -> dict:
    """Get details of a specific user by ID.

    Args:
        user_id: User ID in Seerr
    """
    return get(f"/user/{user_id}")


@mcp.tool()
def seerr_user_quota(user_id: int) -> dict:
    """Get quota information for a specific user.

    Args:
        user_id: User ID in Seerr
    """
    return get(f"/user/{user_id}/quota")


# ─── Issues ──────────────────────────────────────────────────────────────────

@mcp.tool()
def seerr_list_issues(
    filter: str | None = None,
    page: int = 1,
    take: int = 20,
) -> dict:
    """List all issues (report problems with media).

    Args:
        filter: Filter by status: 'open', 'resolved', 'ignored'
        page: Page number (default 1)
        take: Items per page (default 20)
    """
    params = {"page": page, "take": take}
    if filter:
        params["filter"] = filter
    return get("/issue", params)


@mcp.tool()
def seerr_create_issue(
    media_id: int,
    issue_type: int,
    status: int = 0,
    comment: str | None = None,
    reported_by: int | None = None,
) -> dict:
    """Create a new issue for a media item.

    Args:
        media_id: Seerr media ID
        issue_type: Issue type ID (e.g. 1=missing, 2=other, 3=quality, 4=tags, 5=series)
        status: Issue status (0=open, 1=resolved, 2=ignored; default 0)
        comment: Description of the issue
        reported_by: User ID of the reporter
    """
    body = {
        "mediaId": media_id,
        "issueType": issue_type,
        "status": status,
    }
    if comment:
        body["comment"] = comment
    if reported_by is not None:
        body["reportedBy"] = reported_by
    return post("/issue", body)


# ─── Watchlist ───────────────────────────────────────────────────────────────

@mcp.tool()
def seerr_add_watchlist(tmdb_id: int, media_type: str, watchlist_type: str = "movie") -> dict:
    """Add media to the Plex watchlist (syncs to Seerr).

    Args:
        tmdb_id: TMDB ID of the item
        media_type: 'movie' or 'tv'
        watchlist_type: 'movie' or 'show' (for Plex compatibility)
    """
    body = {
        "mediaType": media_type,
        "mediaId": tmdb_id,
        "watchlistType": watchlist_type,
    }
    return post("/watchlist", body)


@mcp.tool()
def seerr_remove_watchlist(tmdb_id: int) -> dict:
    """Remove media from the Plex watchlist.

    Args:
        tmdb_id: TMDB ID of the item
    """
    return delete(f"/watchlist/{tmdb_id}")


# ─── Blocklist ───────────────────────────────────────────────────────────────

@mcp.tool()
def seerr_list_blocklist() -> list:
    """Get all blocklisted (blacklisted) items."""
    return get("/blocklist")


@mcp.tool()
def seerr_add_blocklist(tmdb_id: int) -> dict:
    """Add a movie to the blocklist (prevent requests).

    Args:
        tmdb_id: TMDB movie ID
    """
    return post("/blocklist", {"mediaId": tmdb_id})


@mcp.tool()
def seerr_remove_blocklist(tmdb_id: int) -> dict:
    """Remove a movie from the blocklist.

    Args:
        tmdb_id: TMDB movie ID
    """
    return delete(f"/blocklist/{tmdb_id}")


# ─── Services (Radarr/Sonarr) ────────────────────────────────────────────────

@mcp.tool()
def seerr_radarr_servers() -> list:
    """Get non-sensitive list of configured Radarr servers."""
    return get("/service/radarr")


@mcp.tool()
def seerr_sonarr_servers() -> list:
    """Get non-sensitive list of configured Sonarr servers."""
    return get("/service/sonarr")


@mcp.tool()
def seerr_radarr_server_info(radarr_id: int) -> dict:
    """Get Radarr server quality profiles and root folders.

    Args:
        radarr_id: Radarr server ID in Seerr
    """
    return get(f"/service/radarr/{radarr_id}")


@mcp.tool()
def seerr_sonarr_server_info(sonarr_id: int) -> dict:
    """Get Sonarr server quality profiles and root folders.

    Args:
        sonarr_id: Sonarr server ID in Seerr
    """
    return get(f"/service/sonarr/{sonarr_id}")


@mcp.tool()
def seerr_sonarr_lookup(tmdb_id: int) -> dict:
    """Look up a TV series in Sonarr by TMDB ID to find matching series info.

    Args:
        tmdb_id: TMDB TV show ID
    """
    return get(f"/service/sonarr/lookup/{tmdb_id}")


if __name__ == "__main__":
    mcp.run()
