#!/usr/bin/env python3
import os
import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("SeerrMCP")

SEERR_URL = os.environ.get("SEERR_URL", "http://localhost:5055")
SEERR_KEY = os.environ.get("SEERR_API_KEY", "")

def get_headers():
    return {"X-Api-Key": SEERR_KEY}

@mcp.tool()
def seerr_list_requests() -> list:
    """List media requests in Seerr / Overseerr."""
    try:
        res = httpx.get(f"{SEERR_URL}/api/v1/request", headers=get_headers(), timeout=10)
        return res.json()
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def seerr_search(query: str) -> list:
    """Search movies or TV shows in Seerr / Overseerr."""
    try:
        res = httpx.get(f"{SEERR_URL}/api/v1/search", headers=get_headers(), params={"query": query}, timeout=10)
        return res.json()
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def seerr_get_pending_requests() -> list:
    """Get pending media requests awaiting approval in Seerr / Overseerr."""
    try:
        res = httpx.get(f"{SEERR_URL}/api/v1/request", headers=get_headers(), params={"filter": "pending"}, timeout=10)
        return res.json()
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    mcp.run()
