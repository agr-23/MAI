

from fastapi import APIRouter, HTTPException

import pandas as pd
import json

router = APIRouter(tags=["datos"])

df_paraderos = pd.read_csv("data/paraderos/ruta_041_paradas_suaves_coords.csv")
paraderos_cache = df_paraderos.to_dict(orient="list")

with open("data/rutas/rutas.json","r") as f:
    rutas = json.load(f)


@router.get("/paraderos")
async def paraderos():
    """
        Returns a list of stops across the route 041
        (dict){
            "lat":[], ... list of floats
            "lon":[], ... list of floats
            "direccion":[] ... list of names for all the 

        }
    """    
    return paraderos_cache

@router.get("/ruta")
async def ruta():
    """
        Returns the polyline for the route 041
        (dict){
            "lat":[], ... list of floats
            "lon":[], ... list of floats
            "direccion":[] ... list of names for all the 

        }
    """
    return {
                "041":rutas["041"]
            }

@router.get("/rutas")
async def ruta():
    """
        Returns the polyline for the route 041
        (dict){
            "lat":[], ... list of floats
            "lon":[], ... list of floats
            "direccion":[] ... list of names for all the 

        }
    """
    return rutas

@router.get("/ciclorrutas")
async def ciclorrutas():
    """
        Returns the polyline for the route 041
        (dict){
            "coords":[[]], ... list of lists containing polylines

        }
    """
    with open("data/otros/ciclorutas_coords.json","r") as f:
        ciclorrutas = json.load(f)
    return ciclorrutas

@router.get("/red_peatonal")
async def red_peatonal():
    """
        Returns the polyline for the pedestrian sidewalks
        (dict){
            "coords":[[]], ... list of lists containing polylines

        }
    """
    with open("data/otros/red_peatonal_coords.json","r") as f:
        peatonal = json.load(f)
    return peatonal
