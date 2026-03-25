
import httpx

from fastapi import APIRouter, HTTPException

import pandas as pd

router = APIRouter(tags=["paraderos"])

df_paraderos = pd.read_csv("data/paraderos/ruta_041_paradas_suaves_coords.csv")
data_cache = df_paraderos.to_dict(orient="list")

@router.get("/paraderos")
async def paraderos():
    """
        Returns the paraderos json
        (disct){
            "lat":[], ... list of floats
            "lon":[], ... list of floats
            "direccion":[] ... list of names for all the 

        }
    """    
    return data_cache
