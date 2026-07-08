from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone
from typing import List
import logic

app = FastAPI(
    title="DharmaPath API",
    description="Geospatial constraint API for Nashik Kumbh Mela 2027 processions.",
    version="1.0.0"
)

class Coordinate(BaseModel):
    lat: float
    lon: float

class RouteRequest(BaseModel):
    route: List[Coordinate]
    timestamp: str 

class EmergencyRequest(BaseModel):
    route: List[Coordinate]
    timestamp: str
    vehicle_type: str = "AMBULANCE"

class SimulateEventRequest(BaseModel):
    name: str
    start_lat: float
    start_lon: float
    end_lat: float
    end_lon: float
    duration_minutes: int = 60

@app.get("/")
def root():
    return {"service": "DharmaPath", "status": "active", "docs": "/docs"}

@app.get("/map/landmarks")
def get_landmarks():
    """Returns valid Kumbh coordinates to prevent agent hallucination."""
    return {"landmarks": logic.LANDMARKS}

@app.get("/corridors/active")
def get_active_corridors(time: str):
    """Returns corridors active at the given ISO timestamp."""
    try:
        check_time = datetime.fromisoformat(time.replace("Z", "+00:00"))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid time format. Use ISO 8601.")
        
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
    return logic.is_route_clear(route_dicts, check_time)

@app.post("/emergency/breach")
def request_breach(request: EmergencyRequest):
    """Requests an emergency micro-window to cross a sacred corridor."""
    try:
        check_time = datetime.fromisoformat(request.timestamp.replace("Z", "+00:00"))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid timestamp format.")
        
    route_dicts = [p.dict() for p in request.route]
    return logic.calculate_emergency_breach(route_dicts, check_time)

@app.post("/admin/simulate_event")
def simulate_event(request: SimulateEventRequest):
    """Injects a temporary sacred corridor for sandbox testing."""
    now = datetime.now(timezone.utc)
    end_time = now + timedelta(minutes=request.duration_minutes)
    
    temp_corridor = {
        "id": f"TEMP-{len(logic.CORRIDORS) + 1}",
        "name": request.name,
        "start_time": now.isoformat(),
        "end_time": end_time.isoformat(),
        "waypoints": [
            {"lat": request.start_lat, "lon": request.start_lon},
            {"lat": request.end_lat, "lon": request.end_lon}
        ],
        "width_meters": 50,
        "priority": "CRITICAL"
    }
    
    logic.CORRIDORS.append(temp_corridor)
    
    return {
        "status": "EVENT_INJECTED",
        "message": f"Simulated '{request.name}' active for {request.duration_minutes} mins.",
        "test_instruction": "Call /route/validate with these coords to see CONFLICT."
    }

@app.get("/environmental/status")
def get_environmental_status(weather: str = "CLEAR"):
    """Adjusts corridor safety parameters based on weather."""
    multiplier = 1.0
    risk = "LOW"
    
    if weather.upper() == "RAIN":
        multiplier, risk = 1.5, "MEDIUM"
    elif weather.upper() == "FOG":
        multiplier, risk = 2.0, "HIGH"
        
    return {
        "weather": weather.upper(),
        "risk_level": risk,
        "width_multiplier": multiplier,
        "msg": f"Safety buffers increased by {int((multiplier-1)*100)}% due to {weather}."
    }