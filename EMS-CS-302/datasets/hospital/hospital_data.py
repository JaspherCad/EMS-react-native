import requests
import pandas as pd
from time import sleep

# Step 1: Define known hospitals (fallback)
known_hospitals = [
    {'name': 'Amang Rodriguez Memorial Medical Center', 'latitude': 14.636102, 'longitude': 121.098444, 'Level': None},
    {'name': 'Garcia General Hospital', 'latitude': 14.651220, 'longitude': 121.110939, 'Level': None},
    {'name': 'Saint Anthony Medical Center', 'latitude': 14.624501, 'longitude': 121.102796, 'Level': None},
    {'name': 'SDS Medical Center', 'latitude': 14.639426, 'longitude': 121.110105, 'Level': None},
    {'name': 'San Ramon Hospital', 'latitude': 14.644136, 'longitude': 121.117247, 'Level': None},
    {'name': 'Saint Victoria Hospital', 'latitude': 14.642181, 'longitude': 121.094689, 'Level': None},
    {'name': 'St. Vincent Hospital', 'latitude': 14.650954, 'longitude': 121.107627, 'Level': None},
    {'name': 'VT Maternity Hospital', 'latitude': 14.637106, 'longitude': 121.099440, 'Level': None},
    {'name': 'Jesus Immaculate Concepcion Hospital', 'latitude': 14.638366, 'longitude': 121.108958, 'Level': None},
    {'name': 'De Guzman Clinic', 'latitude': 14.657041, 'longitude': 121.106694, 'Level': None},
    {'name': 'Marikina Doctors Hospital and Medical Center', 'latitude': 14.621069, 'longitude': 121.082590, 'Level': None},
    {'name': 'Marikina Valley Medical Center', 'latitude': 14.634896, 'longitude': 121.104121, 'Level': None},
    {'name': 'P. Gonzales Memorial Hospital', 'latitude': 14.649128, 'longitude': 121.098456, 'Level': None}
]

# Step 2: Acquire Hospital Locations using Overpass API
OVERPASS_URL = "https://overpass-api.de/api/interpreter"
MAX_RETRIES = 3
MARİKİNA_BBOX = {'lat_min': 14.60, 'lat_max': 14.68, 'lon_min': 121.07, 'lon_max': 121.13}

# Overpass QL query for active hospitals in Marikina City
overpass_query = """
[out:json][timeout:25];
area["name"="Marikina"]["boundary"="administrative"]["admin_level"="6"]->.searchArea;
(
  node["amenity"="hospital"]["disused"!="yes"]["closed"!="yes"](area.searchArea);
  way["amenity"="hospital"]["disused"!="yes"]["closed"!="yes"](area.searchArea);
  relation["amenity"="hospital"]["disused"!="yes"]["closed"!="yes"](area.searchArea);
  node["healthcare"="hospital"]["disused"!="yes"]["closed"!="yes"](area.searchArea);
  way["healthcare"="hospital"]["disused"!="yes"]["closed"!="yes"](area.searchArea);
  relation["healthcare"="hospital"]["disused"!="yes"]["closed"!="yes"](area.searchArea);
  node["destination"="hospital"]["disused"!="yes"]["closed"!="yes"](area.searchArea);
  way["destination"="hospital"]["disused"!="yes"]["closed"!="yes"](area.searchArea);
  relation["destination"="hospital"]["disused"!="yes"]["closed"!="yes"](area.searchArea);
);
out center;
"""

hospitals = []
seen_names = set()
seen_coords = set()
for attempt in range(MAX_RETRIES):
    try:
        response = requests.get(OVERPASS_URL, params={'data': overpass_query}, timeout=10)
        response.raise_for_status()
        data = response.json()
        for element in data['elements']:
            name = element['tags'].get('name', 'Unnamed').strip()
            lat = element.get('lat') or element.get('center', {}).get('lat')
            lon = element.get('lon') or element.get('center', {}).get('lon')
            if lat and lon:
                lat, lon = float(lat), float(lon)
                if (MARİKİNA_BBOX['lat_min'] <= lat <= MARİKİNA_BBOX['lat_max'] and
                    MARİKİNA_BBOX['lon_min'] <= lon <= MARİKİNA_BBOX['lon_max']):
                    name_lower = name.lower()
                    coord_key = f"{lat:.6f},{lon:.6f}"
                    if name_lower in seen_names or coord_key in seen_coords:
                        continue
                    seen_names.add(name_lower)
                    seen_coords.add(coord_key)
                    hospitals.append({
                        'name': name,
                        'latitude': lat,
                        'longitude': lon,
                        'Level': None
                    })
        break
    except requests.RequestException as e:
        print(f"Attempt {attempt + 1}/{MAX_RETRIES} failed: {e}")
        if attempt < MAX_RETRIES - 1:
            sleep(2)
        else:
            print("Max retries reached. Using fallback data.")

# Step 3: Create DataFrame from OSM data
hospitals_df = pd.DataFrame(hospitals)
if hospitals_df.empty:
    print("No hospitals found via Overpass API. Using known hospital list.")
    hospitals_df = pd.DataFrame(known_hospitals)
else:
    # Merge with known hospitals
    known_df = pd.DataFrame(known_hospitals)
    known_df['name_lower'] = known_df['name'].str.lower()
    hospitals_df['name_lower'] = hospitals_df['name'].str.lower()
    for _, row in known_df.iterrows():
        if row['name_lower'] not in hospitals_df['name_lower'].values:
            # Check proximity to avoid duplicates (<100m)
            if not any(
                ((row['latitude'] - h['latitude'])**2 + (row['longitude'] - h['longitude'])**2)**0.5 < 0.001
                for h in hospitals_df.to_dict('records')
            ):
                hospitals_df = pd.concat([hospitals_df, pd.DataFrame([{
                    'name': row['name'],
                    'latitude': row['latitude'],
                    'longitude': row['longitude'],
                    'Level': None
                }])], ignore_index=True)
    hospitals_df = hospitals_df.drop(columns=['name_lower'], errors='ignore')

# Deduplicate DataFrame by name and coordinates
hospitals_df = hospitals_df.drop_duplicates(subset=['name', 'latitude', 'longitude'], keep='first')
hospitals_df = hospitals_df.reset_index(drop=True)

# Add ID column
hospitals_df['ID'] = range(1, len(hospitals_df) + 1)
hospitals_df = hospitals_df[['ID', 'name', 'latitude', 'longitude', 'Level']]

# Save to CSV
hospitals_df.to_csv("marikina_hospitals.csv", index=False)
print("Hospital Locations:")
print(hospitals_df.to_string(index=False))