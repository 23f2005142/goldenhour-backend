import random
import requests
from geopy.distance import geodesic

def fetch_live_global_infrastructure(lat: float, lon: float, radius_meters: int = 5000):
    overpass_servers = [
        "https://overpass-api.de/api/interpreter",
        "https://lz4.overpass-api.de/api/interpreter",
        "https://overpass.osm.ch/api/interpreter"
    ]
    
    # Expanded Overpass query adding Fire Stations to the search filters
    query = f"""
    [out:json][timeout:15];
    (
    node["amenity"="hospital"](around:{radius_meters},{lat},{lon});
    node["amenity"="police"](around:{radius_meters},{lat},{lon});
    node["emergency"="ambulance_station"](around:{radius_meters},{lat},{lon});
    node["amenity"="fire_station"](around:{radius_meters},{lat},{lon});
    node["shop"="car_repair"](around:{radius_meters},{lat},{lon});
    node["craft"="mechanic"](around:{radius_meters},{lat},{lon});
    );
    out center;
    """
    
    headers = {
        "User-Agent": "Production_GoldenHour_ROADSOS_Engine/3.0",
        "Accept": "application/json"
    }
    
    for url in overpass_servers:
        try:
            response = requests.get(url, params={'data': query}, headers=headers, timeout=6)
            if response.status_code == 200:
                data = response.json()
                hospitals, police, towing, puncture, showrooms = [], [], [], [], []
                
                for element in data.get('elements', []):
                    tags = element.get('tags', {})
                    name = tags.get('name', 'Emergency Service Provider')
                    e_lat = element['lat']
                    e_lon = element['lon']
                    dist = round(geodesic((lat, lon), (e_lat, e_lon)).km, 1)
                    phone = tags.get('phone', tags.get('contact:phone', "Dial 112 / 108"))
                    
                    payload = {"name": name, "lat": e_lat, "lon": e_lon, "distance_km": dist, "phone": phone}
                    amenity = tags.get('amenity')
                    shop = tags.get('shop')
                    
                    if amenity == 'hospital' or tags.get('emergency') == 'ambulance_station':
                        hospitals.append(payload)
                    elif amenity == 'police':
                        police.append(payload)
                    elif shop == 'car_repair' or tags.get('craft') == 'mechanic':
                        if random.choice([True, False]): puncture.append(payload)
                        else:
                            towing.append(payload)
                            showrooms.append(payload)
                
                return {
                    "status": "success",
                    "data": {
                        "hospitals": sorted(hospitals, key=lambda x: x['distance_km']),
                        "police": sorted(police, key=lambda x: x['distance_km']),
                        "towing": sorted(towing, key=lambda x: x['distance_km']),
                        "puncture": sorted(puncture, key=lambda x: x['distance_km']),
                        "showrooms": sorted(showrooms, key=lambda x: x['distance_km'])
                    }
                }
        except:
            continue
            
    return {"status": "fallback_degradation", "data": {"hospitals": [], "police": [], "towing": [], "puncture": [], "showrooms": []}}