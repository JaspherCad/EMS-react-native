import folium
import webbrowser
import os
import json
import requests

def get_route_geometry(start, end, api_key):
    """Get the detailed route geometry between two points"""
    base_url = "https://api.openrouteservice.org/v2/directions/driving-car/geojson"
    
    # Format coordinates for ORS API (lon,lat format)
    coordinates = [[start[1], start[0]], [end[1], end[0]]]
    
    headers = {
        "Authorization": api_key,
        "Content-Type": "application/json; charset=utf-8"
    }
    
    data = {
        "coordinates": coordinates
    }
    
    try:
        response = requests.post(base_url, headers=headers, json=data)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"API error getting route geometry: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error getting route geometry: {e}")
        return None

def visualize_ems_route(route_data):
    """
    Create an interactive map visualization of the EMS route
    
    Args:
        route_data: Dictionary with route information
    """
    # Unpack route data
    ems_base = route_data['ems_base']
    patient_location = route_data['patient_location']
    hospital_coords = route_data['hospital_coords']
    hospital_name = route_data['hospital_name']
    hospital_level = route_data.get('hospital_level', 'Unknown')
    time_to_patient = route_data['time_to_patient']
    time_to_hospital = route_data['time_to_hospital']
    dispatch_time = route_data.get('dispatch_time', 2)
    on_scene_time = route_data.get('on_scene_time', 10)
    api_key = route_data['api_key']
    
    # Create map centered between the three points
    all_points = [ems_base, patient_location, hospital_coords]
    avg_lat = sum(float(p[0]) for p in all_points) / len(all_points)
    avg_lon = sum(float(p[1]) for p in all_points) / len(all_points)
    
    # Create the map
    m = folium.Map(location=[avg_lat, avg_lon], zoom_start=14, tiles="OpenStreetMap")
    
    # Add markers for each location
    folium.Marker(
        location=ems_base,
        popup="EMS Base (Marikina Rescue 161)",
        icon=folium.Icon(color="red", icon="ambulance", prefix="fa"),
    ).add_to(m)
    
    folium.Marker(
        location=patient_location,
        popup="Patient Location",
        icon=folium.Icon(color="blue", icon="user", prefix="fa"),
    ).add_to(m)
    
    folium.Marker(
        location=hospital_coords,
        popup=f"Hospital: {hospital_name}<br>Level: {hospital_level}",
        icon=folium.Icon(color="green", icon="hospital", prefix="fa"),
    ).add_to(m)
    
    # Create tooltips with detailed time information
    tooltip_ems_to_patient = (
        f"EMS to Patient: {time_to_patient:.2f} minutes<br>"
        f"(after {dispatch_time} min dispatch time)"
    )

    tooltip_patient_to_hospital = (
        f"Patient to Hospital: {time_to_hospital:.2f} minutes<br>"
        f"(after {on_scene_time} min on-scene care)"
    )
    
    # Try to get EMS to Patient route
    ems_to_patient_route = get_route_geometry(ems_base, patient_location, api_key)
    if ems_to_patient_route:
        # Add the GeoJSON to the map
        folium.GeoJson(
            ems_to_patient_route,
            name="EMS to Patient",
            style_function=lambda x: {
                "color": "red",
                "weight": 4,
                "opacity": 0.8
            },
            tooltip=tooltip_ems_to_patient
        ).add_to(m)
    else:
        # Fallback to straight line
        folium.PolyLine(
            locations=[ems_base, patient_location],
            color="red",
            weight=4,
            opacity=0.8,
            tooltip=tooltip_ems_to_patient
        ).add_to(m)
    
    # Try to get Patient to Hospital route
    patient_to_hospital_route = get_route_geometry(patient_location, hospital_coords, api_key)
    if patient_to_hospital_route:
        # Add the GeoJSON to the map
        folium.GeoJson(
            patient_to_hospital_route,
            name="Patient to Hospital",
            style_function=lambda x: {
                "color": "blue",
                "weight": 4,
                "opacity": 0.8
            },
            tooltip=tooltip_patient_to_hospital
        ).add_to(m)
    else:
        # Fallback to straight line
        folium.PolyLine(
            locations=[patient_location, hospital_coords],
            color="blue",
            weight=4,
            opacity=0.8,
            tooltip=tooltip_patient_to_hospital
        ).add_to(m)
    
    # Save the map
    map_file = "./utilities/ems_route.html"
    m.save(map_file)
    
    # Open the map in a web browser
    webbrowser.open('file://' + os.path.realpath(map_file))

if __name__ == "__main__":
    # Read route data from the temporary file
    try:
        with open('temp_route_data.json', 'r') as f:
            route_data = json.load(f)
        
        visualize_ems_route(route_data)
        
        # Clean up the temporary file
        os.remove('temp_route_data.json')
    except FileNotFoundError:
        print("Route data file not found. Please run predict_hospital.py first.")
    except Exception as e:
        print(f"Error visualizing route: {e}")