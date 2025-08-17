import pandas as pd
from datetime import datetime

# Define multiple EMS bases with their locations and names
EMS_BASES = [
    {'base_id': 163, 'base_name': '163 Base - Barangay Hall IVC', 'latitude': 14.6270218, 'longitude': 121.0797032},
    {'base_id': 166, 'base_name': '166 Base - CHO Office, Barangay Sto.niño', 'latitude': 14.6399746, 'longitude': 121.0965973},
    {'base_id': 167, 'base_name': '167 Base - Barangay Hall Kalumpang', 'latitude': 14.624179, 'longitude': 121.0933239},
    {'base_id': 164, 'base_name': '164 Base - DRRMO Building, Barangay Fortune', 'latitude': 14.6628689, 'longitude': 121.1214235},
    {'base_id': 165, 'base_name': '165 Base - St. Benedict Barangay Nangka', 'latitude': 14.6737274, 'longitude': 121.108795},
    {'base_id': 169, 'base_name': '169 Base - Pugad Lawin, Barangay Fortune', 'latitude': 14.6584306, 'longitude': 121.1312048}
]

# Define multiple EMS bases with their locations and names
EMS_BASES = [
    {'base_id': 163, 'base_name': '163 Base - Barangay Hall IVC'},
    {'base_id': 166, 'base_name': '166 Base - CHO Office, Barangay Sto.niño'},
    {'base_id': 167, 'base_name': '167 Base - Barangay Hall Kalumpang'},
    {'base_id': 164, 'base_name': '164 Base - DRRMO Building, Barangay Fortune'},
    {'base_id': 165, 'base_name': '165 Base - St. Benedict Barangay Nangka'},
    {'base_id': 169, 'base_name': '169 Base - Pugad Lawin, Barangay Fortune'}
]

START_TIME = '2025-05-13 08:00:00'

ems = []
ems_id = 1

for base in EMS_BASES:
    num_ambulances = 2 if base['base_id'] in [163, 166, 167] else 1
    
    for i in range(num_ambulances):
        ems.append({
            'ems_id': ems_id,
            'type': 'Ambulance',
            'base_id': base['base_id'],
            'base_name': base['base_name'],
            'base_latitude': base['latitude'],
            'base_longitude': base['longitude'],
            'status': 'Available',
            'last_available_time': START_TIME
        })
        ems_id += 1
    
    ems.append({
        'ems_id': ems_id,
        'type': 'Rescue',
        'base_id': base['base_id'],
        'base_name': base['base_name'],
        'base_latitude': base['latitude'],
        'base_longitude': base['longitude'],
        'status': 'Available',
        'last_available_time': START_TIME
    })
    ems_id += 1

# Save to CSV
ems_df = pd.DataFrame(ems)
ems_df.to_csv('./datasets/ems/marikina_ems.csv', index=False)
print("EMS Dataset (Marikina Multiple Bases):")
print(ems_df.to_string(index=False))