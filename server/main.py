"""
Application entry point.

Creates the FastAPI instance, attaches CORS middleware, and registers all
routers from the app package.  Business logic lives in app/api/routers/,
app/services/, app/models/, and app/utils/ — not here.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.routers.datos_router import router as datos_router
from app.api.routers.bus_router import router as bus_router
from app.api.routers.usuario_router import router as usuario_router

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

app.include_router(datos_router)
app.include_router(bus_router)
app.include_router(usuario_router)
