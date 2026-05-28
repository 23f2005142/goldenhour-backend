from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from database import fetch_live_global_infrastructure

app = FastAPI(title="GoldenHour Global Emergency API Router")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"status": "operational", "system": "GoldenHour Core Engine v3.0"}

@app.get("/api/emergency")
async def get_emergency_infrastructure(lat: float, lon: float, radius: int = 5000):
    if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
        raise HTTPException(status_code=400, detail="Invalid GPS coordinate boundaries.")
    
    result = fetch_live_global_infrastructure(lat, lon, radius)
    return result