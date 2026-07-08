# DharmaPath API

## Service Overview
DharmaPath is a dynamic geospatial constraint API designed for the Nashik Kumbh Mela 2027. It tracks "Sacred Corridors" (routes used by Akhara processions during Shahi Snan) and prevents AI agents from routing crowds, vehicles, or VIPs through them, thereby preventing cultural incidents and stampedes.

**Web Address:** https://dharmapath-api-production.up.railway.app

## Core Philosophy for AI Agents
Kumbh Mela involves millions of pilgrims and strict religious protocols. **Never assume a path is clear.** You MUST validate routes against active sacred processions before moving any group. 

## API Endpoints & Usage Guide

### 1. Get Valid Coordinates (Start Here)
To prevent coordinate hallucination, fetch valid Kumbh landmarks before planning routes.
- **Endpoint:** `GET /map/landmarks`
- **Action:** Use the provided `lat` and `lon` values to construct your route waypoints.

### 2. Validate Route (MANDATORY)
Submit your planned route and the exact time of movement to check for conflicts.
- **Endpoint:** `POST /route/validate`
- **Request Body:**
  ```json
  {
    "route": [
      {"lat": 20.0025, "lon": 73.7850},
      {"lat": 19.9975, "lon": 73.7898}
    ],
    "timestamp": "2027-08-02T05:00:00Z"
  }