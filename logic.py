import math
from datetime import datetime, timezone
from typing import List, Dict, Any

# --- Geospatial Math (Haversine) ---
def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance in meters between two lat/lon points."""
    R = 6371000  # Earth radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

# --- Hardcoded Kumbh Data (The "Sacred" State) ---
LANDMARKS = {
    "Ram Kund": {"lat": 19.9975, "lon": 73.7898},
    "Panchavati": {"lat": 20.0025, "lon": 73.7850},
    "Gangapur Dam": {"lat": 19.9450, "lon": 73.8100},
    "Tapovan": {"lat": 20.0100, "lon": 73.7750},
    "Sita Gufa": {"lat": 20.0050, "lon": 73.7800},
}

# Akhara Procession Corridors (Active during Shahi Snan)
# A corridor is a sequence of waypoints with a specific width (radius_meters)
CORRIDORS = [
    {
        "id": "COR-001",
        "name": "Juna Akhara Procession Route",
        "start_time": "2027-08-02T04:00:00Z",
        "end_time": "2027-08-02T08:00:00Z",
        "waypoints": [
            LANDMARKS["Panchavati"],
            LANDMARKS["Sita Gufa"],
            LANDMARKS["Ram Kund"]
        ],
        "width_meters": 50, # 50 meter wide sacred corridor
        "priority": "HIGH"
    },
    {
        "id": "COR-002",
        "name": "Niranjani Akhara Procession Route",
        "start_time": "2027-08-02T08:30:00Z",
        "end_time": "2027-08-02T12:30:00Z",
        "waypoints": [
            LANDMARKS["Tapovan"],
            LANDMARKS["Panchavati"],
            LANDMARKS["Ram Kund"]
        ],
        "width_meters": 50,
        "priority": "HIGH"
    }
]

# --- Core Validation Logic ---
def is_route_clear(route_points: List[Dict[str, float]], check_time: datetime) -> Dict[str, Any]:
    """
    Checks if a proposed route intersects with any active sacred corridors.
    """
    conflicts = []
    conflicting_corridor_ends = [] # Track end times to calculate wait duration
    
    for corridor in CORRIDORS:
        # Check time overlap
        start = datetime.fromisoformat(corridor["start_time"].replace("Z", "+00:00"))
        end = datetime.fromisoformat(corridor["end_time"].replace("Z", "+00:00"))
        
        # If the check_time is within the corridor's active window
        if start <= check_time <= end:
            # Check spatial overlap
            for point in route_points:
                for wp in corridor["waypoints"]:
                    dist = haversine(point["lat"], point["lon"], wp["lat"], wp["lon"])
                    if dist <= corridor["width_meters"]:
                        conflicts.append({
                            "corridor_id": corridor["id"],
                            "corridor_name": corridor["name"],
                            "conflict_point": point,
                            "distance_to_center_meters": round(dist, 2)
                        })
                        if end not in conflicting_corridor_ends:
                            conflicting_corridor_ends.append(end)
                        break # No need to check other waypoints for this point
                        
    if conflicts:
        # Calculate the earliest time the route will be clear
        earliest_clear_time = min(conflicting_corridor_ends)
        wait_seconds = (earliest_clear_time - check_time).total_seconds()
        wait_minutes = int(wait_seconds / 60) + 1 # Add 1 minute buffer for safety

        return {
            "status": "CONFLICT", 
            "conflicts": conflicts,
            "ai_agent_instructions": {
                "action": "HALT_AND_REROUTE",
                "estimated_wait_minutes": wait_minutes,
                "reason": "Sacred procession in progress. Do not attempt to cross.",
                "suggested_next_step": f"Wait until {earliest_clear_time.isoformat()} or request an alternative route from the Navigation API."
            }
        }
    else:
        return {"status": "CLEAR", "message": "Route is safe. No active sacred processions intersect."}
    

def calculate_emergency_breach(route_points: List[Dict[str, float]], check_time: datetime) -> Dict[str, Any]:
    """
    Calculates a micro-window for an emergency vehicle to cross a sacred corridor.
    """
    # Find the active corridor blocking the route
    active_corridor = None
    for corridor in CORRIDORS:
        start = datetime.fromisoformat(corridor["start_time"].replace("Z", "+00:00"))
        end = datetime.fromisoformat(corridor["end_time"].replace("Z", "+00:00"))
        if start <= check_time <= end:
            active_corridor = corridor
            break
            
    if not active_corridor:
        return {"status": "NO_CORRIDOR_ACTIVE", "message": "No corridor blocking. Proceed normally."}
        
    # Simulate calculating a gap in the procession (e.g., every 15 mins there is a 45 sec gap)
    # In a real system, this would use live IoT data. Here we simulate a safe window.
    wait_time_seconds = 120 # Wait 2 mins for the next gap
    crossing_time_seconds = 15 # Cross quickly
    
    return {
        "status": "BREACH_GRANTED",
        "corridor_name": active_corridor["name"],
        "instructions": {
            "wait_seconds": wait_time_seconds,
            "crossing_window_seconds": crossing_time_seconds,
            "action": f"Halt for {wait_time_seconds}s. Sirens ON. Cross at max speed within {crossing_time_seconds}s window."
        }
    }