from pydantic import BaseModel

class coords(BaseModel):
    latitude: float
    longitude: float
    profile: str = "foot-walking"

class Waypoint(BaseModel):
    latitude: float
    longitude: float

class paradero(BaseModel):
    waypoint: Waypoint
    ubicacion: str
