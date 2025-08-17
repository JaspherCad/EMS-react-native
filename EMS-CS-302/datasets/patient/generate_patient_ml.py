import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from math import radians, sin, cos, sqrt, atan2

def haversine_distance(coord1, coord2):
    """Calculate the great-circle distance between two points on Earth in km,
    with a correction factor to approximate road distances."""
    R = 6371  # Earth's radius in kilometers
    lat1, lon1 = map(radians, coord1)
    lat2, lon2 = map(radians, coord2)
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    direct_distance = R * c
    
    # Apply correction factor based on distance to approximate road distance
    if direct_distance < 1:
        road_factor = 1.4  # Very short distances have more deviation
    elif direct_distance < 3:
        road_factor = 1.35
    elif direct_distance < 5:
        road_factor = 1.3
    else:
        road_factor = 1.25  # Longer distances tend to have more direct routes
    
    return direct_distance * road_factor

# Load hospital dataset
hospitals = pd.read_csv('./datasets/hospital/hospital_dataset (cleaned).csv')
hospitals['location'] = hospitals[['Latitude', 'Longtitude']].values.tolist()
hospitals = hospitals.rename(columns={'ID': 'id', 'Level': 'level', 'Has ER': 'has_er'})
hospitals = hospitals[['id', 'Name', 'Address', 'level', 'location', 'has_er']].to_dict('records')

# Define EMS bases directly since there might be issues with the CSV structure
EMS_BASES = [
    {'base_id': 163, 'base_name': '163 Base - Barangay Hall IVC', 'latitude': 14.6270218, 'longitude': 121.0797032},
    {'base_id': 166, 'base_name': '166 Base - CHO Office, Barangay Sto.niño', 'latitude': 14.6399746, 'longitude': 121.0965973},
    {'base_id': 167, 'base_name': '167 Base - Barangay Hall Kalumpang', 'latitude': 14.624179, 'longitude': 121.0933239},
    {'base_id': 164, 'base_name': '164 Base - DRRMO Building, Barangay Fortune', 'latitude': 14.6628689, 'longitude': 121.1214235},
    {'base_id': 165, 'base_name': '165 Base - St. Benedict Barangay Nangka', 'latitude': 14.6737274, 'longitude': 121.108795},
    {'base_id': 169, 'base_name': '169 Base - Pugad Lawin, Barangay Fortune', 'latitude': 14.6584306, 'longitude': 121.1312048}
]

# Initialize EMS units
START_TIME = datetime(2025, 5, 13, 8, 0, 0)
ems = []
ems_id = 1

# Create EMS units for each base
for base in EMS_BASES:
    # Add 2 ambulances to bases 163, 166, 167
    num_ambulances = 2 if base['base_id'] in [163, 166, 167] else 1
    
    for i in range(num_ambulances):
        ems.append({
            'ems_id': ems_id,
            'type': 'Ambulance',
            'base_id': base['base_id'],
            'base_name': base['base_name'],
            'base_latitude': base['latitude'],
            'base_longitude': base['longitude'],
            'base_location': [base['latitude'], base['longitude']],
            'status': 'Available',
            'last_available_time': START_TIME
        })
        ems_id += 1
    
    # Add 1 rescue vehicle to each base
    ems.append({
        'ems_id': ems_id,
        'type': 'Rescue',
        'base_id': base['base_id'],
        'base_name': base['base_name'],
        'base_latitude': base['latitude'],
        'base_longitude': base['longitude'],
        'base_location': [base['latitude'], base['longitude']],
        'status': 'Available',
        'last_available_time': START_TIME
    })
    ems_id += 1

# Parameters
NUM_PATIENTS = 6000
MARIKINA_BBOX = {'lat_min': 14.60, 'lat_max': 14.68, 'lon_min': 121.07, 'lon_max': 121.13}
SEVERITY_WEIGHTS = {'low': 0.5, 'medium': 0.3, 'high': 0.2}
CONDITIONS = {
    'low': ['Minor injury', 'Fever', 'Laceration'],
    'medium': ['Fracture', 'Moderate respiratory distress', 'Abdominal pain'],
    'high': ['Heart attack', 'Major trauma', 'Stroke']
}
AVERAGE_SPEED = 30  # km/h

# Generate patient data with EMS simulation
np.random.seed(42)
patients = []
current_time = START_TIME
for i in range(NUM_PATIENTS):
    # Generate random patient location within Marikina
    lat = np.random.uniform(MARIKINA_BBOX['lat_min'], MARIKINA_BBOX['lat_max'])
    lon = np.random.uniform(MARIKINA_BBOX['lon_min'], MARIKINA_BBOX['lon_max'])
    patient_location = [lat, lon]
    
    # Assign severity and condition
    severity = np.random.choice(['low', 'medium', 'high'], p=[SEVERITY_WEIGHTS['low'], SEVERITY_WEIGHTS['medium'], SEVERITY_WEIGHTS['high']])
    condition = np.random.choice(CONDITIONS[severity])
    
    # Simulate call time
    time_offset = timedelta(minutes=np.random.randint(5, 15))
    call_time = current_time + time_offset
    
    # Find available ambulance from the closest base
    available_ems = [unit for unit in ems if unit['status'] == 'Available' and unit['type'] == 'Ambulance' 
                     and unit['last_available_time'] <= call_time]
    
    if not available_ems:
        next_available = min([unit['last_available_time'] for unit in ems if unit['type'] == 'Ambulance'])
        call_time = max(call_time, next_available)
        available_ems = [unit for unit in ems if unit['status'] == 'Available' and unit['type'] == 'Ambulance']
    
    # Find closest EMS base to patient location
    ems_distances = []
    for unit in available_ems:
        distance = haversine_distance(unit['base_location'], patient_location)
        ems_distances.append((unit, distance))
    
    # Select the closest available ambulance
    ems_unit, distance_to_patient = min(ems_distances, key=lambda x: x[1])
    ems_unit['status'] = 'Dispatched'
    
    # Calculate response time to patient
    time_to_patient = (distance_to_patient / AVERAGE_SPEED) * 60
    
    # Select hospital
    min_level = {'low': 1, 'medium': 3, 'high': 3}[severity]
    available_hospitals = [h for h in hospitals if h['level'] >= min_level]
    
    if available_hospitals:
        # Use haversine method (with correction factors)
        if severity == 'low':
            # Prefer Level 1 hospitals for low severity (70% chance)
            level_1_hospitals = [h for h in available_hospitals if h['level'] == 1]
            if level_1_hospitals and np.random.random() < 0.7:
                distances = [(h, haversine_distance(patient_location, h['location'])) for h in level_1_hospitals]
            else:
                distances = [(h, haversine_distance(patient_location, h['location'])) for h in available_hospitals]
        else:
            distances = [(h, haversine_distance(patient_location, h['location'])) for h in available_hospitals]
        
        hospital, distance_to_hospital = min(distances, key=lambda x: x[1])
        hospital_id = hospital['id']
        time_to_hospital = (distance_to_hospital / AVERAGE_SPEED) * 60
    else:
        hospital_id = None
        distance_to_hospital = None
        time_to_hospital = 0
    
    # Calculate total response time
    dispatch_time = 2  # minutes
    on_scene_time = 10  # minutes
    handover_time = 5   # minutes
    response_time = dispatch_time + time_to_patient + on_scene_time + time_to_hospital + handover_time
    
    # Calculate total distance traveled
    total_distance_km = distance_to_patient
    if distance_to_hospital is not None:
        total_distance_km += distance_to_hospital
    
    # Update EMS status
    ems_unit['status'] = 'Available'
    ems_unit['last_available_time'] = call_time + timedelta(minutes=response_time)
    
    # Store patient data
    patients.append({
        'patient_id': i + 1,
        'latitude': lat,
        'longitude': lon,
        'severity': severity,
        'condition': condition,
        'Call_Time': call_time.strftime('%Y-%m-%d %H:%M:%S'),
        'hospital_id': hospital_id,
        'distance_to_patient_km': distance_to_patient,
        'distance_to_hospital_km': distance_to_hospital,
        'total_distance_km': total_distance_km,  # Fixed potential error with None values
        'response_time_min': response_time,
        'ems_base_id': ems_unit['base_id'],
        'ems_base_name': ems_unit['base_name'],
        'distance_method': 'haversine'  # Normalized name
    })
    
    current_time = call_time

# Create DataFrame and save
patients_df = pd.DataFrame(patients)
patients_df = patients_df[['patient_id', 'latitude', 'longitude', 'severity', 'condition', 
                           'Call_Time', 'hospital_id', 'distance_to_hospital_km', 
                           'total_distance_km', 'response_time_min', 'ems_base_id', 'ems_base_name']]
patients_df.to_csv('./datasets/patient/marikina_patients_ml_full.csv', index=False)
print("Patient Dataset for ML (first 10 rows):")
print(patients_df.head(10).to_string(index=False))

# Also save a version without the EMS base info to a different file
patients_df_simple = patients_df.drop(['ems_base_id', 'ems_base_name'], axis=1)
patients_df_simple.to_csv('./datasets/patient/marikina_patients_ml.csv', index=False)

# Save the EMS data for reference
ems_df = pd.DataFrame(ems)
ems_df.to_csv('./datasets/ems/marikina_ems_generated.csv', index=False)

print("Dataset generation complete!")