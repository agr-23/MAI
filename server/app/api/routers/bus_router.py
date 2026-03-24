from fastapi import APIRouter, HTTPException

from app.api.external.ors_client import fetch_ors_route
from app.core.config import settings

router = APIRouter(tags=["fleet"])

