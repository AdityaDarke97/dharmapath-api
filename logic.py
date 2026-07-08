import math
from datetime import datetime
from typing import List, Dict, Any

# Haversine formula for geospatial distance
def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371000 
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)

    a = math.sin(d_phi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

# Hardcoded Kumbh landmarks
LANDMARKS = {
    "Ram Kund": {"lat": 19.9975, "lon": 73.7898},
    "Panchavati": {"lat": 20.0025, "lon": 73.7850},
    "Gangapur Dam": {"lat": 19.9450, "lon": 73.8100},
    "Tapovan": {"lat": 20.0100, "lon": 73.7750},
    "Sita Gufa": {"lat": 20.0050, "lon": 73.7800},
}

# TODO: Move this to a Postgres DB with PostGIS for production
CORRIDORS = [
    {
        "id": "COR-001",
        "name": "Juna Akhara Procession Route",
        "start_time": "2027-08-02T04:00:00Z",
        "end_time": "2027-08-02T08:00:00Z",
        "waypoints": [LANDMARKS["Panchavati"], LANDMARKS["Sita Gufa"], LANDMARKS["Ram Kund"]],
        "width_meters": 50,
        "priority": "HIGH"
    },
    {
        "id": "COR-002",
        "name": "Niranjani Akhara Procession Route",
        "start_time": "2027-08-02T08:30:00Z",
        "end_time": "2027-08-02T12:30:00Z",
        "waypoints": [LANDMARKS["Tapovan"], LANDMARKS["Panchavati"], LANDMARKS["Ram Kund"]],
        "width_meters": 50,
        "priority": "HIGH"
    }
]

def is_route_clear(route_points: List[Dict[str, float]], check_time: datetime) -> Dict[str, Any]:
    conflicts = []
    active_ends = [] 
    
    for corridor in CORRIDORS:
        start = datetime.fromisoformat(corridor["start_time"].replace("Z", "+00:00"))
        end = datetime.fromisoformat(corridor["end_time"].replace("Z", "+00:00"))
        
        if start <= check_time <= end:
            for point in route_points:
                for wp in corridor["waypoints"]:
                    dist = haversine(point["lat"], point["lon"], wp["lat"], wp["lon"])
                    if dist <= corridor["width_meters"]:
                        conflicts.append({
                            "corridor_id": corridor["id"],
                            "corridor_name": corridor["name"],
                            "conflict_point": point,
                            "distance_m": round(dist, 2)
                        })
                        if end not in active_ends:
                            active_ends.append(end)
                        break
                        
    if conflicts:
        earliest_clear = min(active_ends)
        wait_mins = int((earliest_clear - check_time).total_seconds() / 60) + 1

        return {
            "status": "CONFLICT", 
            "conflicts": conflicts,
            "ai_agent_instructions": {
                "action": "HALT_AND_REROUTE",
                "estimated_wait_minutes": wait_mins,
                "reason": "Sacred procession active.",
                "next_step": f"Wait until {earliest_clear.isoformat()} or request alt route."
            }
        }
    
    return {"status": "CLEAR", "message": "Route clear."}

def calculate_emergency_breach(route_points: List[Dict[str, float]], check_time: datetime) -> Dict[str, Any]:
    active_corridor = None
    for corridor in CORRIDORS:
        start = datetime.fromisoformat(corridor["start_time"].replace("Z", "+00:00"))
        end = datetime.fromisoformat(corridor["end_time"].replace("Z", "+00:00"))
        if start <= check_time <= end:
            active_corridor = corridor
            break
            
    if not active_corridor:
        return {"status": "NO_CORRIDOR_ACTIVE", "message": "Proceed normally."}
        
    return {
        "status": "BREACH_GRANTED",
        "corridor_name": active_corridor["name"],
        "instructions": {
            "wait_seconds": 120,
            "crossing_window_seconds": 15,
            "action": "Halt 120s. Sirens ON. Cross within 15s window."
        }
    }