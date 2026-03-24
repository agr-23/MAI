"""
Application entry point.

Creates the FastAPI instance, attaches CORS middleware, and registers all
routers from the app package.  Business logic lives in app/api/routers/,
app/services/, app/models/, and app/utils/ — not here.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings

app = FastAPI(
    title="Aplicación de Movilidad",
    description=(
        "API for mobility app"
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
