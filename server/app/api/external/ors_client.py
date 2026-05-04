"""
HTTP client wrappers for the OpenRouteService (ORS) API.
"""

import json
from typing import Any, Dict, List, Tuple

import httpx
from fastapi import HTTPException

async def fetch_ors_route(
    client: httpx.AsyncClient,
    token: str,
    coords: List[Tuple[float, float]],
    steps: bool,
    profile:str
) -> Dict[str, Any]:
    """Request a route from ORS and return the first (best) feature dict."""
    headers = {"Authorization": token, "Content-Type": "application/json"}

    payload: Dict[str, Any] = {
        "coordinates": coords,
        "instructions": steps,
        "geometry": True,
    }

    url = "https://api.openrouteservice.org/v2/directions/driving-car/geojson"
    resp = await client.post(url, headers=headers, json=payload)

    if resp.status_code >= 400:
        try:
            print("ORS ERROR:", resp.status_code, resp.text[:500])
        except Exception:
            pass
        try:
            err = resp.json()
        except Exception:
            err = {"message": resp.text}
        raise HTTPException(status_code=resp.status_code, detail=err)

    gj = resp.json()
    feats = gj.get("features", []) or []

    if not feats:
        return {"geometry": {"type": "LineString", "coordinates": []}, "summary": {}, "alternatives": []}

    principal = feats[0]

    return principal


async def fetch_elevation(
    client: httpx.AsyncClient,
    token: str,
    coords: List[Tuple[float, float]],
) -> List[Tuple[float, float, float]]:
    """Fetch elevation data from ORS for a list of [lon, lat] coordinates."""
    url = "https://api.openrouteservice.org/elevation/line"
    headers = {"Authorization": token, "Content-Type": "application/json"}

    geometry_latlng = [(lng, lat) for lng, lat in coords]
    payload = {
        "format_in": "polyline",
        "format_out": "geojson",
        "geometry": geometry_latlng,
    }

    response = await client.post(url, headers=headers, json=payload)
    if response.status_code != 200:
        raise Exception(f"Elevation API error: {response.text}")

    data = response.json()
    return data["geometry"]["coordinates"]