from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import routes_health, routes_visits  # note the dot

app = FastAPI(title="ClinicFlow Backend")

origins = [
    "http://localhost:5173",  # Vite dev server
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