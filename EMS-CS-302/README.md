<!-- @format -->

# EMS Route Optimization and Hospital Selection System

## Project Description

This Emergency Medical Services (EMS) Route Optimization and Hospital Selection System is a comprehensive healthcare simulation platform designed to predict the optimal hospital for emergency patients while calculating accurate response times using real-world road networks. The system integrates machine learning with geospatial routing to create a decision support tool for emergency medical services.

## Key Features

### 1. Machine Learning Hospital Selection

The system uses a high-accuracy Random Forest model (97% accuracy) to recommend the most appropriate hospital based on:

- Patient location (latitude/longitude coordinates)
- Medical condition severity (low, medium, high)
- Specific medical condition (9 different emergency types)
- Distance to hospital and expected response times

### 2. Real-Time Route Calculation

- Integrates with OpenRouteService API to calculate actual road network distances
- Automatically falls back to straight-line (haversine) calculations when needed
- Accounts for geographic obstacles, one-way streets, and road networks

### 3. Comprehensive Response Time Modeling

The system provides detailed time breakdowns reflecting real-world EMS operations:

- Dispatch time (initial call processing and crew mobilization)
- Travel time to patient location
- On-scene assessment and stabilization time
- Transport time to hospital
- Hospital handover time

### 4. Interactive Visualization

- Generates dynamic HTML maps showing the complete emergency route
- Displays EMS bases, patient location, and selected hospital
- Shows actual road network paths with time estimates
- Includes tooltips with detailed timing information

### 5. Flexible Input System

- Accepts user-defined patient locations within a specified geographic area
- Validates input coordinates against municipal boundaries
- Allows selection from standardized medical conditions and severity levels

## Model Performance

The hospital selection Random Forest model achieves exceptional performance:

- **Accuracy**: 97%
- **Cross-validation accuracy**: 97% ± 1%
- **Model reproduction rate**: 99.38% of original hospital assignments

### Feature Importance

| Feature                   | Importance |
| ------------------------- | ---------- |
| Longitude                 | 0.311792   |
| Latitude                  | 0.296327   |
| Severity                  | 0.165625   |
| Distance to Hospital (km) | 0.110070   |
| Response Time (min)       | 0.083226   |
| Condition                 | 0.032961   |

## Technologies Used

- **Python**: Core programming language
- **Pandas/NumPy**: Data handling and numerical computations
- **Scikit-learn**: Machine learning model training and prediction
- **Folium**: Interactive map visualization
- **OpenRouteService API**: Road network routing and travel time estimation
- **JSON**: Data transfer between program components

## Applications

This system has potential applications in:

- Emergency services planning and dispatch
- Hospital resource allocation
- EMS response time optimization
- Patient outcome improvement through faster, more appropriate hospital selection
- Training and education for emergency medical personnel
- Public health policy planning for emergency services coverage

## How to Use

1. **Install the required libraries**
      ```bash
      pip install pandas numpy scikit-learn folium requests
      ```
2. **Setup the data**
      - Run marikina_ems.py to initialize hospital data
      - Run generate_patient_ml.py to generate training dataset
      - Run train_model.py to train the hospital prediction model
3. **Get an OpenRouteService API key**
      - Sign up at OpenRouteService
      - Add your API key to predict_hospital.py
4. **Run the prediction system**
      ```bash
      python predict_hospital.py
      ```
5. **Enter patient details when prompted**
      - Use Google Maps to get accurate latitude/longitude coordinates
      - Select severity level (low, medium, high)
      - Choose the appropriate medical condition
6. **Review the prediction results**

      - The system will show the recommended hospital with distance and timing
      - Example output:

      ```
      === Hospital Prediction Results ===
      Predicted hospital ID: 2
      Predicted hospital: Amang Rodriguez Memorial Medical Center
      Hospital Level: 3
      Estimated distance to hospital: 1.23 km

      Response Time Breakdown:
      • Dispatch time: 2.00 minutes
      • Travel to patient: 3.73 minutes
      • On-scene time: 10.00 minutes
      • Transport to hospital: 2.40 minutes
      • Hospital handover: 5.00 minutes
      • Total response time: 23.13 minutes

      Responding EMS Base: 167 Base - Barangay Hall Kalumpang
      Distance to patient: 0.85 km

      ✓ Using real road network distances and times with OpenRouteService API

      Do you want to visualize the route? (y/n):
      ```

7. **Visualize the emergency route**
      - Answer 'y' to open an interactive map in your web browser
      - The map will show the complete route from EMS base to patient to hospital

## Future Work

Potential improvements include:

- Real-time traffic integration
- Dynamic ambulance positioning optimization
- Multi-patient incident handling
- Integration with hospital capacity systems
