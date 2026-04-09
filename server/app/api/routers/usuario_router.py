import httpx
from fastapi import APIRouter, HTTPException

from app.api.external.ors_client import fetch_ors_route
from app.api.routers.datos_router import paraderos_cache
from app.models.schemas import coords
from app.core.config import settings
from app.utils.functions import haversine_km

router = APIRouter(tags=["user"])

paraderos = paraderos_cache

@router.post("/near_paradero")
async def get_near_paradero(location:coords):
    if not paraderos:
        raise HTTPException(status_code=500, detail="Paraderos not found")

    origen_lat = location.latitude
    origen_lon = location.longitude
    destino_lat = paraderos[0]["lat"]
    destino_lon = paraderos[0]["lon"]

    for paradero in paraderos:
        dist1 = haversine_km(lat1=origen_lat, lon1=origen_lon,
                             lat2=destino_lat, lon2=destino_lon)
        dist2 = haversine_km(lat1=origen_lat, lon1=origen_lon,
                             lat2=paradero["lat"], lon2=paradero["lon"])
        if dist2 < dist1:
            destino_lat = paradero["lat"]
            destino_lon = paradero["lon"]

    # ORS espera coordenadas en orden [lon, lat]
    coords = [[origen_lon, origen_lat], [destino_lon, destino_lat]]
    async with httpx.AsyncClient(timeout=30) as client:
        try:
            r = await fetch_ors_route(
                client=client,
                token=settings.ORS_TOKEN,
                coords=coords,
                steps=False,
            )
        except httpx.RequestError as exc:
            raise HTTPException(status_code=502, detail=f"ORS network error: {exc!s}")
        
    if not r or "geometry" not in r:
        raise HTTPException(status_code=500, detail="Unexpected ORS response (no geometry)")

    return {
        "geometry": r.get("geometry",{})
        }

