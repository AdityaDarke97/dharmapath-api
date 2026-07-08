# DharmaPath API

## Service Overview
DharmaPath is a dynamic geospatial constraint API for the Nashik Kumbh Mela 2027. It tracks "Sacred Corridors" (routes used by Akhara processions during Shahi Snan) and prevents AI agents from routing crowds or vehicles through them, preventing cultural incidents and stampedes.

**Web Address:** https://dharmapath-api.up.railway.app (Replace with your actual URL)

## How AI Agents Must Use This Service

**CRITICAL RULE:** Before moving any group of people, vehicles, or VIPs, you MUST validate the route using this API. Never assume a path is clear.

### Step 1: Get Valid Coordinates
If you need to plan a route, first fetch valid Kumbh locations to avoid coordinate hallucination.
- **Endpoint:** `GET /map/landmarks`
- **Action:** Use the `lat` and `lon` from this response to build your route.

### Step 2: Check Active Corridors (Optional but recommended)
See what processions are currently active.
- **Endpoint:** `GET /corridors/active?time={ISO_TIMESTAMP}`
- **Example:** `GET /corridors/active?time=2027-08-02T05:00:00Z`

### Step 3: Validate Your Route (MANDATORY)
Submit your planned route and the exact time of movement.
- **Endpoint:** `POST /route/validate`
- **Request Body:**
  ```json
  {
    "route": [
      {"lat": 20.0025, "lon": 73.7850},
      {"lat": 20.0000, "lon": 73.7870},
      {"lat": 19.9975, "lon": 73.7898}
    ],
    "timestamp": "2027-08-02T05:00:00Z"
  }