

from fastapi import APIRouter, HTTPException

import pandas as pd
import json

router = APIRouter(tags=["datos"])

with open("data/otros/paraderos.json","r") as f:
    paraderos_cache = json.load(f)

with open("data/rutas/rutas.json","r") as f:
    rutas_data = json.load(f)

@router.get("/paraderos")
def get_paraderos():
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
def ruta():
    """
        Returns the polyline for the route 041
        (dict){
            "lat":[], ... list of floats
            "lon":[], ... list of floats
            "direccion":[] ... list of names for all the 

        }
    """
    return {
                "041":rutas_data["041"]
            }

@router.get("/rutas")
def rutas():
    """
        Returns the polyline for the route 041
        (dict){
            "lat":[], ... list of floats
            "lon":[], ... list of floats
            "direccion":[] ... list of names for all the 

        }
    """
    return rutas_data

@router.get("/ciclorrutas")
def ciclorrutas():
    """
        Returns the polyline for the route 041
        (dict){
            "coords":[[]], ... list of lists containing polylines

        }
    """
    with open("data/otros/ciclorutas_coords.json","r") as f:
        ciclorrutas_data = json.load(f)
    return ciclorrutas_data

@router.get("/red_peatonal")
def red_peatonal():
    """
        Returns the polyline for the pedestrian sidewalks
        (dict){
            "coords":[[]], ... list of lists containing polylines

        }
    """
    with open("data/otros/red_peatonal_coords.json","r") as f:
        peatonal = json.load(f)
    return peatonal

@router.get("/semaforos")
def semaforos():
    """
        Returns the polyline for the pedestrian sidewalks
        (dict){
            "coords":[[]], ... list of lists containing polylines

        }
    """
    with open("data/otros/semaforos_041.json","r") as f:
        semaforos = json.load(f)
    return semaforos