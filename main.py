from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
from typing import List, Dict
import logic

app = FastAPI(
    title="DharmaPath API",
    description="Dynamic Sacred Corridor & Procession De-confliction for Nashik Kumbh Mela 2027",
    version="1.0.0"
)

# --- Pydantic Models for strict AI parsing ---
class Coordinate(BaseModel):
    lat: float
    lon: float

class RouteRequest(BaseModel):
    route: List[Coordinate]
    timestamp: str  # ISO 8601 format

class EmergencyRequest(BaseModel):
    route: List[Coordinate]
    timestamp: str
    vehicle_type: str = "AMBULANCE"

# --- Endpoints ---

@app.get("/")
def root():
    return {"service": "DharmaPath API", "status": "active", "docs": "/docs"}

@app.get("/map/landmarks")
def get_landmarks():
    """
    SECRET WEAPON: Returns valid Kumbh coordinates so AI agents don't hallucinate.
    """
    return {"landmarks": logic.LANDMARKS}

@app.get("/corridors/active")
def get_active_corridors(time: str):
    """Returns all corridors active at the given ISO timestamp."""
    try:
        check_time = datetime.fromisoformat(time.replace("Z", "+00:00"))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid time format. Use ISO 8601 (e.g., 2027-08-02T05:00:00Z)")
        
    active = []
    for c in logic.CORRIDORS:
        start = datetime.fromisoformat(c["start_time"].replace("Z", "+00:00"))
        end = datetime.fromisoformat(c["end_time"].replace("Z", "+00:00"))
        if start <= check_time <= end:
            active.append(c)
            
    return {"timestamp": time, "active_corridors": active}

@app.post("/route/validate")
def validate_route(request: RouteRequest):
    """Validates if a proposed route is safe at a specific time."""
    try:
        check_time = datetime.fromisoformat(request.timestamp.replace("Z", "+00:00"))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid timestamp format.")
        
    route_dicts = [p.dict() for p in request.route]
    result = logic.is_route_clear(route_dicts, check_time)
    return result

@app.post("/emergency/breach")
def request_breach(request: EmergencyRequest):
    """Requests an emergency micro-window to cross a sacred corridor."""
    try:
        check_time = datetime.fromisoformat(request.timestamp.replace("Z", "+00:00"))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid timestamp format.")
        
    route_dicts = [p.dict() for p in request.route]
    result = logic.calculate_emergency_breach(route_dicts, check_time)
    return result