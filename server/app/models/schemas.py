from pydantic import BaseModel

class waypoint(BaseModel):
    latitude:float
    longitude:float

class paradero(BaseModel):
    waypoint:waypoint
    ubicacion:str