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
        "coordinates": [[MKAD_LON, MKAD_LAT], [lon, lat]],  # [долгота, широта]
        "format": "geojson"
    }
    async with httpx.AsyncClient(timeout=10) as client:
        try:
            r = await client.post(url, headers=headers, json=json_data)
            if r.status_code != 200:
                error_detail = r.json().get("error", {}).get("message", r.text)
                raise HTTPException(status_code=500, detail=f"ORS API error: {error_detail}")
            
            data = r.json()
            
            # Проверяем наличие маршрута
            if "features" not in data or len(data["features"]) == 0:
                raise HTTPException(status_code=500, detail="No route found between points")
            
            feature = data["features"][0]
            if "properties" not in feature or "segments" not in feature["properties"]:
                raise HTTPException(status_code=500, detail="Invalid route structure")
            
            segments = feature["properties"]["segments"]
            if not segments or "distance" not in segments[0]:
                raise HTTPException(status_code=500, detail="Distance not found in route")
            
            distance_m = segments[0]["distance"]
            return {"distance_km": round(distance_m / 1000)}
        
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail=f"Network error: {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
