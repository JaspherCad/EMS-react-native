import pandas as pd
import folium
from folium.plugins import MarkerCluster

# Load datasets
patients = pd.read_csv('./datasets/patient/marikina_patients_ml.csv')
hospitals = pd.read_csv('./datasets/hospital/hospital_dataset (cleaned).csv')

# Use EMS bases directly instead of loading from CSV
EMS_BASES = [
    {'base_id': 163, 'base_name': '163 Base - Barangay Hall IVC', 'latitude': 14.6270218, 'longitude': 121.0797032},
    {'base_id': 166, 'base_name': '166 Base - CHO Office, Barangay Sto.niño', 'latitude': 14.6399746, 'longitude': 121.0965973},
    {'base_id': 167, 'base_name': '167 Base - Barangay Hall Kalumpang', 'latitude': 14.624179, 'longitude': 121.0933239},
    {'base_id': 164, 'base_name': '164 Base - DRRMO Building, Barangay Fortune', 'latitude': 14.6628689, 'longitude': 121.1214235},
    {'base_id': 165, 'base_name': '165 Base - St. Benedict Barangay Nangka', 'latitude': 14.6737274, 'longitude': 121.108795},
    {'base_id': 169, 'base_name': '169 Base - Pugad Lawin, Barangay Fortune', 'latitude': 14.6584306, 'longitude': 121.1312048}
]

# Create map centered on Marikina City
marikina_center = [14.64, 121.10]  
m = folium.Map(location=marikina_center, zoom_start=13, tiles='OpenStreetMap')

# Add patient locations (blue markers with clustering)
marker_cluster = MarkerCluster().add_to(m)
for _, row in patients.iterrows():
    folium.CircleMarker(
        location=[row['latitude'], row['longitude']],
        radius=5,
        color='blue',
        fill=True,
        fill_color='blue',
        fill_opacity=0.6,
        popup=f"Patient {row['patient_id']}: {row['severity']}, {row['condition']}"
    ).add_to(marker_cluster)

# Add hospital locations (red markers)
for _, row in hospitals.iterrows():
    folium.Marker(
        location=[row['Latitude'], row['Longtitude']],
        popup=f"Hospital {row['ID']}: {row['Name']} (Level {row['Level']})",
        icon=folium.Icon(color='red', icon='hospital', prefix='fa')
    ).add_to(m)

# Add EMS base locations (green markers)
for base in EMS_BASES:
    folium.Marker(
        location=[base['latitude'], base['longitude']],
        popup=f"{base['base_name']}",
        icon=folium.Icon(color='green', icon='ambulance', prefix='fa')
    ).add_to(m)

# Save and display map
m.save('./datasets/patient/map_marikina_patients_ml.html')
print("Map saved as map_marikina_patients_ml.html. Open in a browser to view.")