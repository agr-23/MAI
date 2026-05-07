from fastapi import APIRouter, HTTPException
from app.models.schemas import paradero

import pandas as pd
import json
from sklearn.neighbors import BallTree
import numpy as np

router = APIRouter(tags=["paraderos"])

# Read and cast historic data
historic = pd.read_csv("data/rutas/clean_historic.csv")
historic["horaregistro"] = pd.to_timedelta(historic["horaregistro"])

ruta_coords_rad = np.radians(historic[["latitud", "longitud"]].values)
    
# Data structure for log(n) geospatial queries
tree = BallTree(ruta_coords_rad, metric="haversine")

EARTH_RADIUS_M = 6_371_000  # meters

@router.post("/buses_proximos")
async def buses_proximos(paradero: paradero):
    current_hour = pd.to_datetime(pd.Timestamp.now()).hour

    hora_horas = historic["horaregistro"].dt.total_seconds() // 3600
    historic_hour_filtered = historic[hora_horas.between(current_hour - 2, current_hour)]

    # Ampliar ventana si no hay registros en la hora actual (ej. madrugada)
    if historic_hour_filtered.empty:
        historic_hour_filtered = historic

    fecha_most_records = historic_hour_filtered["fecha"].value_counts().idxmax()

    historic_hour_filtered = historic_hour_filtered[historic_hour_filtered["fecha"] == fecha_most_records]

    coord = np.radians([[paradero.waypoint.latitude, paradero.waypoint.longitude]])

    distances, indices = tree.query(coord, k=3)

    nearest_buses = historic.iloc[indices[0]]

    # Pasar distancias a distancia euclidiana, y dividir sobre 60 km/h en promedio, para obtener distancia aproximada
    times = (distances[0] * EARTH_RADIUS_M) / 16.6

    return {
        "paradero":paradero.ubicacion,
        "buses_proximos":nearest_buses.placavehiculo.unique().tolist(),
        "tiempos":times.tolist(),
        "ubicaciones":nearest_buses[["latitud","longitud"]].to_dict(orient="records")
    }