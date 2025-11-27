import requests
from typing import Dict, Any

class OpenMeteoProvider:
    GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
    WEATHER_URL = "https://api.open-meteo.com/v1/forecast"

    @staticmethod
    def geocode(q: str) -> Dict[str, float]:
        params = {"name": q, "count": 1, "language": "es", "format": "json"}
        r = requests.get(OpenMeteoProvider.GEOCODE_URL, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
        if not data.get("results"):
            raise ValueError("Ciudad no encontrada")
        first = data["results"][0]
        return {
            "lat": first["latitude"],
            "lon": first["longitude"],
            "name": first["name"],
        }

    @staticmethod
    def get_current_weather(lat: float, lon: float) -> Dict[str, Any]:
        params = {
            "latitude": lat,
            "longitude": lon,
            "current_weather": True,
            "hourly": "relative_humidity_2m",
            "timezone": "auto",
        }
        r = requests.get(OpenMeteoProvider.WEATHER_URL, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()

        current = data.get("current_weather", {})
        temp_c = current.get("temperature")

        # humedad alineada al time del current_weather, si existe
        humidity = None
        try:
            t = current.get("time")
            times = data["hourly"]["time"]
            hums = data["hourly"]["relative_humidity_2m"]
            idx = times.index(t)
            humidity = hums[idx]
        except Exception:
            pass

        return {
            "temp_c": temp_c,
            "humidity": humidity,
            "condition": weather_code_to_text(current.get("weathercode")),
            "wind_kph": current.get("windspeed"),
            "updated_at": current.get("time"),
        }

def weather_code_to_text(code: int) -> str:
    mapping = {
        0:"Despejado",1:"Mayormente despejado",2:"Parcialmente nublado",3:"Nublado",
        45:"Niebla",48:"Escarcha",51:"Llovizna ligera",53:"Llovizna",55:"Llovizna intensa",
        61:"Lluvia ligera",63:"Lluvia",65:"Lluvia intensa",80:"Chaparrones",95:"Tormenta",
    }
    return mapping.get(code, f"Código {code}")
