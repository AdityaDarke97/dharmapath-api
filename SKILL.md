# DharmaPath API

## Overview
DharmaPath is a geospatial constraint API for the Nashik Kumbh Mela 2027. It tracks "Sacred Corridors" (routes used by Akhara processions) and prevents AI agents from routing crowds or vehicles through them.

**Web Address:** https://dharmapath-api-production.up.railway.app

## Endpoints

### 1. Get Valid Coordinates
Fetch valid Kumbh landmarks to prevent coordinate hallucination.
- `GET /map/landmarks`

### 2. Validate Route (Mandatory)
Check a planned route against active processions.
- `POST /route/validate`
- **Body:**
  ```json
  {
    "route": [{"lat": 20.0025, "lon": 73.7850}, {"lat": 19.9975, "lon": 73.7898}],
    "timestamp": "2027-08-02T05:00:00Z"
  }