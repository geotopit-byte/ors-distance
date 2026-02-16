from fastapi import FastAPI, HTTPException
import httpx

app = FastAPI()

ORS_KEY = "eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6IjBmN2FhMjMwYjEwNjQ4NGI5MmIzNmY0ODI3ZWI3NDBjIiwiaCI6Im11cm11cjY0In0="
MKAD_LON = 38.008771
MKAD_LAT = 55.792861

@app.get("/road-distance")
async def road_distance(lat: float, lon: float):
    url = "https://api.openrouteservice.org/v2/directions/driving-car"
    headers = {
        "Authorization": ORS_KEY,
        "Content-Type": "application/json"
    }
    json_data = {
        "coordinates": [[MKAD_LON, MKAD_LAT], [lon, lat]],
        "format": "geojson"
    }
    async with httpx.AsyncClient(timeout=10) as client:
        try:
            r = await client.post(url, headers=headers, json=json_data)
            if r.status_code != 200:
                error_msg = r.json().get("error", {}).get("message", "Unknown error")
                raise HTTPException(status_code=500, detail=f"ORS API error: {error_msg}")
            
            data = r.json()
            if "routes" not in data or len(data["routes"]) == 0:
                raise HTTPException(status_code=500, detail="No route found between points")
            
            distance_m = data["routes"][0]["summary"]["distance"]
            return {"distance_km": round(distance_m / 1000)}
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
