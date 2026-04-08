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

    destino = [paraderos[0]["lon"], paraderos[0]["lat"]]
    origen = [location.longitude, location.latitude]

    for paradero in paraderos:
        dist1 = haversine_km(lat1=origen[0],lon1=origen[1],
                             lat2=destino[0],lon2=destino[1])
        
        dist2 = haversine_km(lat1=origen[0],lon1=origen[1],
                             lat2=paradero["lat"],lon2=paradero["lon"])
        if dist1 > dist2:
            destino = [paradero["lon"], paradero["lat"]]

    coords = [origen, destino]
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

