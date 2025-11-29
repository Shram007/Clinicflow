from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import routes_visits, routes_health

app = FastAPI(title="ClinicFlow Backend")

# CORS – allow frontend
origins = [
    "http://localhost:5173",  # Vite default
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes_health.router, prefix="/api")
app.include_router(routes_visits.router, prefix="/api")