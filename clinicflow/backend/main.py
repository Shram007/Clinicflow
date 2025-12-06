from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from pathlib import Path

from .api import routes_health, routes_visits
from .api import routes_voice

def _load_env():
    env_path = Path(__file__).resolve().parents[1] / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            if "=" in s:
                k, v = s.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

_load_env()

app = FastAPI(title="ClinicFlow Backend")

# For now, allow all origins so CORS never blocks you in dev
origins_env = os.environ.get("ALLOWED_ORIGINS", "*")
origins = [o.strip() for o in origins_env.split(",") if o.strip()] or ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

 
app.include_router(routes_health.router, prefix="/api")
app.include_router(routes_visits.router, prefix="/api")
app.include_router(routes_voice.router, prefix="/api")
