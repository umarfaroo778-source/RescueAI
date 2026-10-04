from datetime import datetime, timezone
import requests

UA = "RescueAI-Hackathon-MVP/1.0"

def ts():
    return datetime.now(timezone.utc).isoformat()

def geocode(location):
    if not location.strip():
        return {"ok":False, "error":"Location not provided.", "hospitals":[]}
    try:
        r = requests.get("https://nominatim.openstreetmap.org/search",
                         params={"q":location,"format":"json","limit":1},
                         headers={"User-Agent":UA}, timeout=8)
        r.raise_for_status()
        data = r.json()
        if not data:
            return {"ok":False, "error":"Location could not be resolved.", "hospitals":[]}
        x = data[0]
        return {"ok":True, "name":x.get("display_name",location),
                "lat":float(x["lat"]), "lon":float(x["lon"]),
                "source":"OpenStreetMap Nominatim","fetched_at":ts(),"hospitals":[]}
    except Exception as e:
        return {"ok":False, "error":f"Geocoding failed: {e}", "hospitals":[]}

def nearby_hospitals(lat, lon):
    try:
        q = '''[out:json][timeout:10];
        (node["amenity"="hospital"](around:5000,%s,%s);
         way["amenity"="hospital"](around:5000,%s,%s);
         relation["amenity"="hospital"](around:5000,%s,%s););
        out center tags;''' % (lat,lon,lat,lon,lat,lon)
        r = requests.post("https://overpass-api.de/api/interpreter",
                          data=q, headers={"User-Agent":UA}, timeout=15)
        r.raise_for_status()
        out = []
        for e in r.json().get("elements", [])[:8]:
            name = e.get("tags", {}).get("name")
            if name: out.append(name)
        return out
    except Exception:
        return []

def weather(lat, lon):
    try:
        r = requests.get("https://api.open-meteo.com/v1/forecast",
                         params={"latitude":lat,"longitude":lon,
                                 "current":"temperature_2m,rain,wind_speed_10m",
                                 "timezone":"auto"}, timeout=8)
        r.raise_for_status()
        c = r.json()["current"]
        return {"ok":True,"temperature_c":c.get("temperature_2m"),
                "rain_mm":c.get("rain"),"wind_kmh":c.get("wind_speed_10m"),
                "observed_at":c.get("time"),"fetched_at":ts()}
    except Exception as e:
        return {"ok":False,"error":f"Weather unavailable: {e}"}
