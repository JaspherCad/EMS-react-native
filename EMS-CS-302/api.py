from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, validator
import pickle
import pandas as pd
import numpy as np
import json
import os
from typing import Dict, List, Optional

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="EMS Hospital Dispatch API",
    description="Predicts EMS routing Tech 101",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# #note:
# 1: what we did? (BLACK BOX METHOD + API INTEGRATION)
# 2: We created a FastAPI application for EMS hospital dispatch predictions.
# 3: We defined data models for requests and responses, including validation.
# 4: BASICALLY COPY PASTED CODE FROM predict_hospital.py + ai guide.
# 5: We set up endpoints for receiving patient data and returning hospital recommendations.
# 6: postman test
# 7: done
# #end-note:


# REQUEST interface DTO

model = None
le_severity = None
le_condition = None
hospitals = None
ems_bases = None

class PredictionRequest(BaseModel):
    latitude: float = Field(..., ge=14.60, le=14.68, description="Patient latitude (14.60-14.68)")
    longitude: float = Field(..., ge=121.07, le=121.13, description="Patient longitude (121.07-121.13)")
    severity: str = Field(..., description="Patient condition severity")
    condition: str = Field(..., description="Patient medical condition")
    


    # MARIKINA_BBOX = {
    #     'lat_min': 14.60,
    #     'lat_max': 14.68,
    #     'lon_min': 121.07,
    #     'lon_max': 121.13
    # }
    
    # # Valid input values
    # VALID_SEVERITIES = ['low', 'medium', 'high']
    # VALID_CONDITIONS = [
    #     'Minor injury', 'Fever', 'Laceration', 
    #     'Fracture', 'Moderate respiratory distress', 'Abdominal pain',  
    #     'Heart attack', 'Major trauma', 'Stroke'  
    # ]
    

    @validator('severity')
    def validate_severity(cls, v):
        valid = ['low', 'medium', 'high']
        if v.lower() not in valid:
            raise ValueError(f"Severity must be one of {valid}")
        return v.lower()
        
    @validator('condition')
    def validate_condition(cls, v):
        valid = ['Minor injury', 'Fever', 'Laceration', 'Fracture', 
                'Moderate respiratory distress', 'Abdominal pain',  
                'Heart attack', 'Major trauma', 'Stroke']
        if v not in valid:
            raise ValueError(f"Condition must be one of: {valid}")
        return v

# Response interface DTO
class TimeComponents(BaseModel):
    dispatch_time: float
    time_to_patient: float
    on_scene_time: float
    time_to_hospital: float
    handover_time: float
    total_time: float

class Hospital(BaseModel):
    id: int
    name: str
    level: str
    coords: List[float]
    distance_km: float

class EMSBase(BaseModel):
    base_id: int
    base_name: str
    coords: List[float]
    distance_km: float
    time_min: float
    is_road_distance: bool

class PredictionResponse(BaseModel):
    hospital: Hospital
    ems_base: EMSBase
    time_components: TimeComponents
    is_fallback_calculation: bool


# #note: refer to predict_hospital.py
# class DistanceCalculator:
def haversine_distance(coord1, coord2):
    """Calculate the great-circle distance between two points on Earth in km."""
    from math import radians, sin, cos, sqrt, atan2
    
    R = 6371 
    lat1, lon1 = map(radians, coord1)
    lat2, lon2 = map(radians, coord2)
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c


# #note: refer to predict_hospital.py
# class DistanceCalculator: except get_route_info

def get_closest_ems_base(patient_location):
    """Find the closest EMS base to the patient."""

    # if not self.ems_bases:
    #         raise ValueError("EMS bases not loaded")
    
    ems_base_distances = []
    print("\nFinding closest EMS base...")

    
    for base in ems_bases:
        base_coords = [base['latitude'], base['longitude']]
        
        # Calculate distance using haversine formula (simplified from get_route_info)
        distance = haversine_distance(base_coords, patient_location)
        
        # Estimate travel time (assuming average speed of 30 km/h like in predict_hospital.py)
        travel_time = (distance / 30) * 60  # Convert to minutes
        
        ems_base_distances.append({
            'base_id': base['base_id'],
            'base_name': base['base_name'],
            'coords': base_coords,
            'distance': distance,
            'time': travel_time,
            'is_road_distance': False  # Using haversine approximation
        })
    
    # Select the closest EMS base
    closest_ems_base = min(ems_base_distances, key=lambda x: x['time'])
    return closest_ems_base
# end-class DistanceCalculator:



# Class HospitalPredictor:

def get_hospital_distances(patient_location):
    """Calculate distances from patient to all hospitals."""
    hospital_info = []
    print("\nCalculating route information...")
    
    for idx, hospital in hospitals.iterrows():
        hospital_coords = hospital['location']
        hospital_id = hospital['ID']
        
        # Calculate distance using haversine formula (simplified from get_route_info)
        distance = haversine_distance(patient_location, hospital_coords)
        
        # Estimate travel time (assuming average speed of 30 km/h like in predict_hospital.py)
        travel_time = (distance / 30) * 60  # Convert to minutes
        
        hospital_info.append((hospital_id, distance, travel_time, False))  # is_fallback_calculation = False
        
        # Sleep to avoid rate limiting if many hospitals (keeping from original)
        # time.sleep(0.1)  # Commented out for API performance
            
    return hospital_info
# end-class HospitalPredictor:

# #end-note: refer to predict_hospital.py




@app.on_event("startup")
async def load_model_and_data():
    """Load model, encoders, and data at startup"""
    global model, le_severity, le_condition, hospitals, ems_bases
    
    try:
        # Load model and encoders
        with open('./models/hospital_prediction_model.pkl', 'rb') as f:
            model = pickle.load(f)
        with open('./models/le_severity.pkl', 'rb') as f:
            le_severity = pickle.load(f)
        with open('./models/le_condition.pkl', 'rb') as f:
            le_condition = pickle.load(f)
            
        # Load hospital dataset for distance calculations (exact same as predict_hospital.py)
        hospitals = pd.read_csv('./datasets/hospital/hospital_dataset (cleaned).csv')
        hospitals['location'] = hospitals[['Latitude', 'Longtitude']].values.tolist()
        
        # Load EMS bases (exact same as predict_hospital.py)
        ems_bases = [
            {'base_id': 163, 'base_name': '163 Base - Barangay Hall IVC', 'latitude': 14.6270218, 'longitude': 121.0797032},
            {'base_id': 166, 'base_name': '166 Base - CHO Office, Barangay Sto.niño', 'latitude': 14.6399746, 'longitude': 121.0965973},
            {'base_id': 167, 'base_name': '167 Base - Barangay Hall Kalumpang', 'latitude': 14.624179, 'longitude': 121.0933239},
            {'base_id': 164, 'base_name': '164 Base - DRRMO Building, Barangay Fortune', 'latitude': 14.6628689, 'longitude': 121.1214235},
            {'base_id': 165, 'base_name': '165 Base - St. Benedict Barangay Nangka', 'latitude': 14.6737274, 'longitude': 121.108795},
            {'base_id': 169, 'base_name': '169 Base - Pugad Lawin, Barangay Fortune', 'latitude': 14.6584306, 'longitude': 121.1312048}
        ]
        
        print("✅ Model, encoders, and data loaded successfully")
        
    except Exception as e:
        print(f"❌ Error loading models and data: {e}")
        raise

@app.get("/")
async def root():
    """API health check"""
    return {
        "message": "EMS Hospital Dispatch API is running",
        "version": "1.0.0",
        "endpoints": {
            "predict": "/predict",
            "docs": "/docs",
            "redoc": "/redoc"
        }
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "encoders_loaded": le_severity is not None and le_condition is not None,
        "hospitals_loaded": hospitals is not None,
        "ems_bases_loaded": ems_bases is not None,
        "total_hospitals": len(hospitals) if hospitals is not None else 0,
        "total_ems_bases": len(ems_bases) if ems_bases is not None else 0
    }



@app.get("/get-all-maps")
async def get_all_maps():
    """Get all hospital and EMS base maps -> turn them into JSON serializable"""


    # POñeta baket kailangan ng i dito??? GMG
    hospitals_list = []
    for i, hospital in hospitals.iterrows(): 
        hospitals_list.append({
            "id": int(hospital['ID']),
            "name": str(hospital['Name']),
            "level": str(hospital.get('Level', 'Unknown')),
            "latitude": float(hospital['Latitude']),
            "longitude": float(hospital['Longtitude']),
            "coords": [float(hospital['Latitude']), float(hospital['Longtitude'])]
        })

        
    ems_bases_list = []
    for base in ems_bases:
        ems_bases_list.append({
            "base_id": int(base['base_id']),
            "base_name": str(base['base_name']),
            "latitude": float(base['latitude']),
            "longitude": float(base['longitude']),
            "coords": [float(base['latitude']), float(base['longitude'])]
        })
    
    return {
        "hospitals": hospitals_list,
        "ems_bases": ems_bases_list
    }

@app.post("/predict", response_model=PredictionResponse)
#sample postman request
# {
#   "latitude": 14.65,
#   "longitude": 121.10,
#   "severity": "medium",
#   "condition": "Fracture"
# }
async def predict_hospital(request: PredictionRequest):
    """Predict optimal hospital and EMS routing for emergency patient"""
    
    if model is None or le_severity is None or le_condition is None:
        raise HTTPException(status_code=500, detail="Models not loaded properly")
    
    try:
        patient_location = [request.latitude, request.longitude]
        
        # Get closest EMS base
        closest_ems_base = get_closest_ems_base(patient_location)
        
        # Get hospital distances
        hospital_info = get_hospital_distances(patient_location)
        
        # Find closest hospital for distance calculation
        closest_hospital = min(hospital_info, key=lambda x: x[1])
        distance_to_hospital_km = closest_hospital[1]
        
        # Calculate response time components
        time_to_patient = closest_ems_base['time']
        time_to_hospital = closest_hospital[2]
        
        # Fixed time components
        dispatch_time = 2.0
        on_scene_time = 10.0
        handover_time = 5.0
        
        # Total response time calculation
        response_time_min = dispatch_time + time_to_patient + on_scene_time + time_to_hospital + handover_time
        
        # Create input DataFrame for model prediction
        new_patient = pd.DataFrame({
            'latitude': [request.latitude],
            'longitude': [request.longitude],
            'severity': [request.severity],
            'condition': [request.condition],
            'distance_to_hospital_km': [distance_to_hospital_km],
            'response_time_min': [response_time_min]
        })
        
        # Encode categorical variables
        try:
            new_patient['severity'] = le_severity.transform(new_patient['severity'])
            new_patient['condition'] = le_condition.transform(new_patient['condition'])
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid severity or condition: {e}")
        
        # Make prediction
        predicted_hospital_id = int(model.predict(new_patient)[0])
        
        # Get hospital information
        hospital_row = hospitals[hospitals['ID'] == predicted_hospital_id]
        if hospital_row.empty:
            raise HTTPException(status_code=404, detail=f"Hospital with ID {predicted_hospital_id} not found")
        
        hospital_row = hospital_row.iloc[0]
        hospital_name = str(hospital_row['Name'])
        hospital_level = str(hospital_row.get('Level', 'Unknown'))
        hospital_coords = [float(hospital_row['location'][0]), float(hospital_row['location'][1])]
        
        # Find predicted hospital in hospital_info
        predicted_hospital_info = next((info for info in hospital_info if info[0] == predicted_hospital_id), None)
        predicted_distance = predicted_hospital_info[1] if predicted_hospital_info else distance_to_hospital_km
        
        # Create response
        response = PredictionResponse(
            hospital=Hospital(
                id=predicted_hospital_id,
                name=hospital_name,
                level=hospital_level,
                coords=hospital_coords,
                distance_km=float(predicted_distance)
            ),
            ems_base=EMSBase(
                base_id=int(closest_ems_base['base_id']),
                base_name=str(closest_ems_base['base_name']),
                coords=[float(c) for c in closest_ems_base['coords']],
                distance_km=float(closest_ems_base['distance']),
                time_min=float(closest_ems_base['time']),
                is_road_distance=bool(closest_ems_base['is_road_distance'])
            ),
            time_components=TimeComponents(
                dispatch_time=float(dispatch_time),
                time_to_patient=float(time_to_patient),
                on_scene_time=float(on_scene_time),
                time_to_hospital=float(time_to_hospital),
                handover_time=float(handover_time),
                total_time=float(response_time_min)
            ),
            is_fallback_calculation=bool(predicted_hospital_info[3] if predicted_hospital_info else True)
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
