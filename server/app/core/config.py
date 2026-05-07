"""
Centralised application settings loaded from environment variables / .env file.

Usage:
    from app.core.config import settings
    token = settings.ORS_TOKEN
"""

import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # External API tokens
    ORS_TOKEN: str = os.getenv("ORS_TOKEN", "")

    # CORS — configurar ALLOWED_ORIGINS en .env para producción
    # Apps móviles (Flutter) no envían Origin, así que * es seguro para esta API
    ALLOWED_ORIGINS: list[str] = [
        o.strip()
        for o in os.getenv("ALLOWED_ORIGINS", "*").split(",")
    ]

    # Server port (informational – used by Dockerfile / uvicorn CLI)
    PORT: int = int(os.getenv("PORT", "8000"))


settings = Settings()
