from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api import routes_health, routes_visits  # no dot if you're running `uvicorn main:app`

app = FastAPI(title="ClinicFlow Backend")

# For now, allow all origins so CORS never blocks you in dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],    
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

 
app.include_router(routes_health.router, prefix="/api")
app.include_router(routes_visits.router, prefix="/api")