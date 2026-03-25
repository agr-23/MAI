from fastapi import APIRouter, HTTPException

import pandas as pd
import json
import random

router = APIRouter(tags=["paraderos"])

with open("data/rutas/rutas.json","r") as f:
    ruta = json.load(f)["041"]

@router.get("/buses_proximos")
async def buses_proximos(paradero:str):
    placas = ['EQS782', 'TSZ911', 'EQS783', 'EQS970', 'EQT626', 'WMQ124',
       'EQR887', 'WMR092', 'EQW266', 'EQT786', 'WMQ211', 'EQT067',
       'FWK922', 'EQT960', 'SMV024', 'EQT153', 'FWK060', 'EQS704',
       'EQT572', 'WMQ475', 'EQT152', 'STV889', 'FWK726', 'EQT896',
       'FWL396', 'EQT038', 'FWL282', 'WMQ199', 'FWK874', 'WMQ799',
       'FVY459', 'WMQ800']

    buses = random.sample(placas, k=3)
    tiempos = sorted(random.sample(range(1,20,2), k=3))
    ubicaciones = random.sample(ruta, k=3)

    return {
        "paradero":paradero,
        "buses_proximos":buses,
        "tiempos":tiempos,
        "ubicaciones":ubicaciones
    }