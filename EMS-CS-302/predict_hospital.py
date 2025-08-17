import pandas as pd
import pickle
import numpy as np
from math import radians, sin, cos, sqrt, atan2
import requests
import time
import subprocess
import json
import os

# #note:
# Latitude (14.60 to 14.68): 14.65
# Longitude (121.07 to 121.13): 121.10
# Severity (low, medium, high): medium
# Condition (Minor injury, Fever, Laceration, Fracture, Moderate respiratory distress, Abdominal pain, Heart attack, Major trauma, Stroke): Fracture
# Do you want to visualize the route? (y/n): y
# #end-note:

class DistanceCalculator:
    """Handles distance calculations between coordinates using different methods."""
    
    def __init__(self, api_key=None, average_speed=30):
        self.api_key = api_key
        self.average_speed = average_speed  # km/h
        self.use_road_network = api_key is not None and api_key != "your_api_key_here"
    
    def haversine_distance(self, coord1, coord2):
        """Calculate the great-circle distance between two points on Earth in km."""
        R = 6371 
        lat1, lon1 = map(radians, coord1)
        lat2, lon2 = map(radians, coord2)
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        return R * c
    
    def get_route_info(self, start_coords, end_coords):
        """Get road distance and duration between two points using OpenRouteService API."""
        if not self.use_road_network:
            # Calculate using haversine if no API key
            distance = self.haversine_distance(start_coords, end_coords)
            time_estimate = (distance / self.average_speed) * 60
            return distance, time_estimate, False
            
        base_url = "https://api.openrouteservice.org/v2/directions/driving-car"
        
        # Format coordinates for ORS API (lon,lat format)
        coordinates = [[start_coords[1], start_coords[0]], [end_coords[1], end_coords[0]]]
        
        headers = {
            "Authorization": self.api_key,
            "Content-Type": "application/json; charset=utf-8" 
        }
        
        data = {
            "coordinates": coordinates
        }
        
        try:
            response = requests.post(base_url, headers=headers, json=data)
            if response.status_code == 200:
                data = response.json()
                # Extract distance (in meters) and duration (in seconds)
                distance_km = data['routes'][0]['summary']['distance'] / 1000
                duration_min = data['routes'][0]['summary']['duration'] / 60
                return distance_km, duration_min, True
            else:
                print(f"API error: {response.status_code}")
                print(f"Response details: {response.text}")
                # Fall back to haversine
                distance = self.haversine_distance(start_coords, end_coords)
                time_estimate = (distance / self.average_speed) * 60
                return distance, time_estimate, False
        except Exception as e:
            print(f"Error getting route information: {e}")
            # Fall back to haversine
            distance = self.haversine_distance(start_coords, end_coords)
            time_estimate = (distance / self.average_speed) * 60
            return distance, time_estimate, False


class HospitalPredictor:
    """Handles hospital prediction based on patient data."""
    
    # Marikina city bounding box
    MARIKINA_BBOX = {
        'lat_min': 14.60,
        'lat_max': 14.68,
        'lon_min': 121.07,
        'lon_max': 121.13
    }
    
    # Valid input values
    VALID_SEVERITIES = ['low', 'medium', 'high']
    VALID_CONDITIONS = [
        'Minor injury', 'Fever', 'Laceration', 
        'Fracture', 'Moderate respiratory distress', 'Abdominal pain',  
        'Heart attack', 'Major trauma', 'Stroke'  
    ]
    
    def __init__(self):
        self.model = None
        self.le_severity = None
        self.le_condition = None
        self.hospitals = None
        self.ems_bases = None
        self.distance_calculator = None
        
    def load_models_and_data(self, api_key=None):
        """Load all required models and data."""
        try:
            # Load model and encoders
            with open('./models/hospital_prediction_model.pkl', 'rb') as f:
                self.model = pickle.load(f)

            with open('./models/le_severity.pkl', 'rb') as f:
                self.le_severity = pickle.load(f)

            with open('./models/le_condition.pkl', 'rb') as f:
                self.le_condition = pickle.load(f)

            # Load hospital dataset for distance calculations
            self.hospitals = pd.read_csv('./datasets/hospital/hospital_dataset (cleaned).csv')
            self.hospitals['location'] = self.hospitals[['Latitude', 'Longtitude']].values.tolist()
            
            # Initialize distance calculator
            self.distance_calculator = DistanceCalculator(api_key=api_key)
            
            # Define EMS bases
            self.ems_bases = [
                {'base_id': 163, 'base_name': '163 Base - Barangay Hall IVC', 'latitude': 14.6270218, 'longitude': 121.0797032},
                {'base_id': 166, 'base_name': '166 Base - CHO Office, Barangay Sto.niño', 'latitude': 14.6399746, 'longitude': 121.0965973},
                {'base_id': 167, 'base_name': '167 Base - Barangay Hall Kalumpang', 'latitude': 14.624179, 'longitude': 121.0933239},
                {'base_id': 164, 'base_name': '164 Base - DRRMO Building, Barangay Fortune', 'latitude': 14.6628689, 'longitude': 121.1214235},
                {'base_id': 165, 'base_name': '165 Base - St. Benedict Barangay Nangka', 'latitude': 14.6737274, 'longitude': 121.108795},
                {'base_id': 169, 'base_name': '169 Base - Pugad Lawin, Barangay Fortune', 'latitude': 14.6584306, 'longitude': 121.1312048}
            ]
            return True
        except Exception as e:
            print(f"Error loading models and data: {e}")
            return False
    
    def get_closest_ems_base(self, patient_location):
        """Find the closest EMS base to the patient."""
        if not self.ems_bases:
            raise ValueError("EMS bases not loaded")
            
        ems_base_distances = []
        print("\nFinding closest EMS base...")
        
        for base in self.ems_bases:
            base_coords = [base['latitude'], base['longitude']]
            
            distance, travel_time, is_road_network = self.distance_calculator.get_route_info(
                base_coords, patient_location
            )
            
            ems_base_distances.append({
                'base_id': base['base_id'],
                'base_name': base['base_name'],

                'coords': base_coords,
                'distance': distance,
                'time': travel_time,
                'is_road_distance': is_road_network
            })
        
        # Select the closest EMS base
        closest_ems_base = min(ems_base_distances, key=lambda x: x['time'])
        return closest_ems_base
    
    def get_hospital_distances(self, patient_location):
        """Calculate distances from patient to all hospitals."""
        if self.hospitals is None:
            raise ValueError("Hospital data not loaded")
            
        hospital_info = []
        print("\nCalculating route information...")
        
        for idx, hospital in self.hospitals.iterrows():
            hospital_coords = hospital['location']
            hospital_id = hospital['ID']
            
            distance, travel_time, is_road_network = self.distance_calculator.get_route_info(
                patient_location, hospital_coords
            )
            hospital_info.append((hospital_id, distance, travel_time, not is_road_network))
            
            # Sleep to avoid rate limiting if many hospitals
            time.sleep(0.1)
            
        return hospital_info
    
    def predict_hospital(self, latitude, longitude, severity, condition, closest_ems_base, hospital_info):
        """Predict the most appropriate hospital."""
        # Find closest hospital for distance calculation
        closest_hospital = min(hospital_info, key=lambda x: x[1])
        distance_to_hospital_km = closest_hospital[1]

        # Calculate response time components
        time_to_patient = closest_ems_base['time']
        time_to_hospital = closest_hospital[2]
        
        # Fixed time components
        dispatch_time = 2 
        on_scene_time = 10  
        handover_time = 5  

        # Total response time calculation
        response_time_min = dispatch_time + time_to_patient + on_scene_time + time_to_hospital + handover_time

        # Create input DataFrame for model
        new_patient = pd.DataFrame({
            'latitude': [latitude],
            'longitude': [longitude],
            'severity': [severity],
            'condition': [condition],
            'distance_to_hospital_km': [distance_to_hospital_km],
            'response_time_min': [response_time_min]
        })

        # Preprocess new data
        new_patient['severity'] = self.le_severity.transform(new_patient['severity'])
        new_patient['condition'] = self.le_condition.transform(new_patient['condition'])

        # Predict hospital
        predicted_hospital_id = self.model.predict(new_patient)[0]
        
        # Get hospital info
        hospital_row = self.hospitals[self.hospitals['ID'] == predicted_hospital_id].iloc[0]

        hospital_name = hospital_row['Name']
        hospital_level = hospital_row['Level'] if 'Level' in self.hospitals.columns else "Unknown"

        hospital_coords = [float(hospital_row['location'][0]), float(hospital_row['location'][1])]
            
            
        # Find predicted hospital in hospital_info
        predicted_hospital_info = next((info for info in hospital_info if info[0] == predicted_hospital_id), None)
        
        result = {
            'hospital_id': int(predicted_hospital_id),
            'hospital_name': hospital_name,
            'hospital_level': hospital_level,
            'hospital_coords': hospital_coords,
            'distance': float(distance_to_hospital_km),
            'time_components': {
                'dispatch_time': float(dispatch_time),
                'time_to_patient': float(time_to_patient),
                'on_scene_time': float(on_scene_time),
                'time_to_hospital': float(time_to_hospital),
                'handover_time': float(handover_time),
                'total_time': float(response_time_min)
            },
            'is_fallback_calculation': bool(predicted_hospital_info[3]) if predicted_hospital_info else True,
            'ems_base': {
                'base_id': int(closest_ems_base['base_id']),
                'base_name': closest_ems_base['base_name'],
                'coords': [float(closest_ems_base['coords'][0]), float(closest_ems_base['coords'][1])],
                'distance_km': float(closest_ems_base['distance']),
                'time_min': float(closest_ems_base['time']),
                'is_road_distance': bool(closest_ems_base['is_road_distance'])
            }
        }
        
        return result
    
    def get_user_input(self):
        """Get and validate user input for prediction."""
        print("Enter patient details for hospital prediction:")

        # Get and validate latitude
        while True:
            try:
                latitude = float(input(f"Latitude ({self.MARIKINA_BBOX['lat_min']} to {self.MARIKINA_BBOX['lat_max']}): "))
                if not (self.MARIKINA_BBOX['lat_min'] <= latitude <= self.MARIKINA_BBOX['lat_max']):
                    print(f"Error: Latitude must be between {self.MARIKINA_BBOX['lat_min']} and {self.MARIKINA_BBOX['lat_max']}.")
                    continue
                break
            except ValueError:
                print("Error: Latitude must be a number.")

        # Get and validate longitude
        while True:
            try:
                longitude = float(input(f"Longitude ({self.MARIKINA_BBOX['lon_min']} to {self.MARIKINA_BBOX['lon_max']}): "))
                if not (self.MARIKINA_BBOX['lon_min'] <= longitude <= self.MARIKINA_BBOX['lon_max']):
                    print(f"Error: Longitude must be between {self.MARIKINA_BBOX['lon_min']} and {self.MARIKINA_BBOX['lon_max']}.")
                    continue
                break
            except ValueError:
                print("Error: Longitude must be a number.")

        # Get and validate severity
        while True:
            severity = input(f"Severity ({', '.join(self.VALID_SEVERITIES)}): ").lower()
            if severity not in self.VALID_SEVERITIES:
                print(f"Error: Severity must be one of {', '.join(self.VALID_SEVERITIES)}.")
                continue
            break

        # Get and validate condition
        while True:
            condition = input(f"Condition ({', '.join(self.VALID_CONDITIONS)}): ")
            if condition not in self.VALID_CONDITIONS:
                print(f"Error: Condition must be one of {', '.join(self.VALID_CONDITIONS)}.")
                continue
            break
            
        return latitude, longitude, severity, condition
    
    def print_results(self, prediction_result):
        """Print prediction results."""
        print(f"\nPredicted hospital ID: {prediction_result['hospital_id']}")
        print(f"Predicted hospital: {prediction_result['hospital_name']}")
        print(f"Hospital Level: {prediction_result['hospital_level']}")
        print(f"Estimated distance to hospital: {prediction_result['distance']:.2f} km")

        # Detailed response time breakdown
        time_components = prediction_result['time_components']
        print("\nResponse Time Breakdown:")
        print(f"• Dispatch time: {time_components['dispatch_time']:.2f} minutes")
        print(f"• Travel to patient: {time_components['time_to_patient']:.2f} minutes")
        print(f"• On-scene time: {time_components['on_scene_time']:.2f} minutes")
        print(f"• Transport to hospital: {time_components['time_to_hospital']:.2f} minutes")
        print(f"• Hospital handover: {time_components['handover_time']:.2f} minutes")
        print(f"• Total response time: {time_components['total_time']:.2f} minutes")

        # Add extra information about the routing method used
        print("\nRouting Information:")
        if self.distance_calculator.use_road_network:
            print("✓ Using real road network distances and times with OpenRouteService API")
            
            if prediction_result['is_fallback_calculation']:
                print("⚠ API fallback used: calculations are based on straight-line approximation")
            
            print(f"EMS base to patient: {time_components['time_to_patient']:.2f} minutes")
            print(f"Patient to hospital: {time_components['time_to_hospital']:.2f} minutes")
        else:
            print("⚠ Using straight-line distance approximations")
            print("  To use real road network, configure an OpenRouteService API key")

        # Print JSON-like summary for frontend mapping
        try:
            # Create a completely new dict with standard Python types
            json_summary = {
                "hospital": {
                    "id": int(prediction_result['hospital_id']),
                    "name": str(prediction_result['hospital_name']),
                    "level": str(prediction_result['hospital_level']),
                    "coords": [float(c) for c in prediction_result['hospital_coords']],
                    "distance_km": float(prediction_result['distance'])
                },
                "ems_base": {
                    "base_id": int(prediction_result['ems_base']['base_id']),
                    "base_name": str(prediction_result['ems_base']['base_name']),
                    "coords": [float(c) for c in prediction_result['ems_base']['coords']],
                    "distance_km": float(prediction_result['ems_base']['distance_km']),
                    "time_min": float(prediction_result['ems_base']['time_min']),
                    "is_road_distance": bool(prediction_result['ems_base']['is_road_distance'])
                },
                "time_components": {
                    k: float(v) for k, v in prediction_result['time_components'].items()
                },
                "is_fallback_calculation": bool(prediction_result.get('is_fallback_calculation', True))
            }
            print("\nJSON-like summary (for frontend):")
            print(json.dumps(json_summary, indent=2))
        except Exception as e:
            print(f"Error printing JSON summary: {e}")
            # Print type info for debugging
            print(f"hospital_id type: {type(prediction_result['hospital_id'])}")


    
    def visualize_route(self, patient_location, prediction_result):
        """Visualize the predicted route."""
        try:
            # Get hospital coordinates
            hospital_coords = self.hospitals[self.hospitals['ID'] == prediction_result['hospital_id']]['location'].iloc[0]
            
            # Write the route data to a temporary file for the visualization script
            route_data = {
                'ems_base': [float(coord) for coord in prediction_result['ems_base']['coords']],
                'ems_base_name': prediction_result['ems_base']['base_name'],
                'patient_location': [float(coord) for coord in patient_location],
                'hospital_coords': [float(coord) for coord in hospital_coords],
                'hospital_name': prediction_result['hospital_name'],
                'hospital_level': str(prediction_result['hospital_level']),
                'time_to_patient': float(prediction_result['time_components']['time_to_patient']),
                'time_to_hospital': float(prediction_result['time_components']['time_to_hospital']),
                'dispatch_time': float(prediction_result['time_components']['dispatch_time']),
                'on_scene_time': float(prediction_result['time_components']['on_scene_time']),
                'api_key': self.distance_calculator.api_key
            }
            
            # Save route data to a temporary file
            try:
                with open('temp_route_data.json', 'w') as f:
                    json.dump(route_data, f)
                
                # Call the visualization script
                print("\nOpening visualization in web browser...")
                subprocess.run(["python", "./utilities/visualize_route.py"])
                
            except TypeError as e:
                print(f"\nError serializing data: {e}")
                # Print problematic values to help debugging
                print("Data types:")
                for key, value in route_data.items():
                    print(f"{key}: {type(value)}")
            
        except Exception as e:
            print(f"\nError visualizing route: {e}")
            print("Make sure visualize_route.py is in the utilities directory.")


def main():
    # API key for OpenRouteService
    ORS_API_KEY = "5b3ce3597851110001cf6248e9e7bf352181406b956089df63e2bb75"
    
    # Initialize predictor
    predictor = HospitalPredictor()
    
    # Load models and data
    if not predictor.load_models_and_data(api_key=ORS_API_KEY):
        print("Failed to load required models and data. Exiting.")
        return
    
    # Get user input
    latitude, longitude, severity, condition = predictor.get_user_input()
    patient_location = [latitude, longitude]
    
    # Find closest EMS base
    closest_ems_base = predictor.get_closest_ems_base(patient_location)
    
    # Display selected EMS base information
    print(f"\nSelected EMS base: {closest_ems_base['base_name']}")
    print(f"Distance to patient: {closest_ems_base['distance']:.2f} km")
    print(f"Estimated travel time: {closest_ems_base['time']:.2f} minutes")
    
    if not closest_ems_base['is_road_distance']:
        print("(Using straight-line distance calculation)")
    
    # Get hospital distances
    hospital_info = predictor.get_hospital_distances(patient_location)
    
    # Make prediction
    prediction_result = predictor.predict_hospital(
        latitude, longitude, severity, condition, closest_ems_base, hospital_info
    )
    
    # Print results
    predictor.print_results(prediction_result)
    
    # Ask user if they want to visualize the results
    while True:
        visualize = input("\nDo you want to visualize the route? (y/n): ").lower()
        if visualize in ['y', 'n']:
            break
        print("Please enter 'y' or 'n'.")

    if visualize == 'y':
        predictor.visualize_route(patient_location, prediction_result)


if __name__ == "__main__":
    main()
