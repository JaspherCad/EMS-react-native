import { Link, Stack, router } from 'expo-router';
import { StyleSheet, Text, View, TextInput, Button, Alert, Platform, Modal, TouchableOpacity } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Picker } from '@react-native-picker/picker';
import { WebView } from 'react-native-webview';
import { useState } from 'react';
import { predict } from '@/apiCalls/api';





// #info: 
/*

1: this is where we predict value.
simple map:
INPUT -> SEND TO API -> OUTPUT

2: Send the output to screen index: 

(tabs)/index have:
[userCoordinates, hospitalCoordinates, routeCoordinates].

then we replace its value with:

[
    [longitude, latitude], 

    [predictedHospitalCoordinates.longitude, predictedHospitalCoordinates.latitude],

    [well, routeCoordinates is computed inside (tabs)/index... so keep that.]

]
*/
// #end-info: 











export default function Predict() {
    const [latitude, setLatitude] = useState('14.65');
    const [longitude, setLongitude] = useState('121.10');
    const [severity, setSeverity] = useState('medium');
    const [condition, setCondition] = useState('Fracture');
    const [showMapModal, setShowMapModal] = useState(false);

    const handlePredict = async () => {
        const lat = parseFloat(latitude);
        const lon = parseFloat(longitude);

        if (isNaN(lat) || isNaN(lon)) {
            Alert.alert('Invalid Input', 'Please enter valid latitude and longitude');
            return;
        }

        const inputData = {
            latitude: lat,
            longitude: lon,
            severity: severity,
            condition: condition
        };
        

        try {
            console.log('Input data:', JSON.stringify(inputData, null, 2));
            const response = await predict(inputData);

            console.log('Prediction response:', response);
            
            // SEND THE PREDICTED DATA AS "PARAMETER"... 
            router.push({
                pathname: '/(tabs)',
                params: {
                    userLat: lat.toString(),
                    userLon: lon.toString(),
                    hospitalLat: response.hospital.coords[0].toString(),
                    hospitalLon: response.hospital.coords[1].toString(),
                    hospitalName: response.hospital.name,
                    hospitalLevel: response.hospital.level,
                    distance: response.hospital.distance_km.toString(),
                    totalTime: response.time_components.total_time.toString(),
                    prediction: 'true'
                }
            });
            
        } catch (error) {
            console.error('Error occurred while predicting:', error);
            Alert.alert('Error', 'Failed to get prediction. Please try again.');
        }


    };

    const handleMapMessage = (event: any) => {
        try {
            const data = JSON.parse(event.nativeEvent.data);
            if (data.type === 'locationSelected') {
                setLatitude(data.lat.toString());
                setLongitude(data.lng.toString());
                setShowMapModal(false);
                Alert.alert('Location Set', `Lat: ${data.lat.toFixed(6)}, Lng: ${data.lng.toFixed(6)}`);
            }
        } catch (error) {
            console.error('Error parsing map message:', error);
        }
    };

    const getMapHTML = () => {
        const currentLat = parseFloat(latitude) || 14.65;
        const currentLng = parseFloat(longitude) || 121.10;

        return `
      <!DOCTYPE html>
      <html>
      <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
        <style>
          body { margin: 0; padding: 0; font-family: Arial, sans-serif; }
          #map { height: calc(100vh - 60px); width: 100vw; }
          #instructions { 
            height: 60px; 
            background: #007AFF; 
            color: white; 
            display: flex; 
            align-items: center; 
            justify-content: center; 
            font-size: 16px; 
            font-weight: bold;
          }
        </style>
        <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
      </head>
      <body>
        <div id="instructions">Tap on the map to select a location</div>
        <div id="map"></div>
        <script>
          const map = L.map('map').setView([${currentLat}, ${currentLng}], 13);
          
          L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors'
          }).addTo(map);
          
          let marker = L.marker([${currentLat}, ${currentLng}]).addTo(map);
          
          map.on('click', function(e) {
            const lat = e.latlng.lat;
            const lng = e.latlng.lng;
            
            // Remove existing marker
            if (marker) {
              map.removeLayer(marker);
            }
            
            // Add new marker
            marker = L.marker([lat, lng]).addTo(map);
            
            // Send coordinates back to React Native
            if (window.ReactNativeWebView) {
              window.ReactNativeWebView.postMessage(JSON.stringify({
                type: 'locationSelected',
                lat: lat,
                lng: lng
              }));
            }
          });
        </script>
      </body>
      </html>
    `;
    };

    return (
        <SafeAreaView style={styles.container}>
            <Text style={styles.title}>Hospital Predictionz</Text>

            <View style={styles.inputContainer}>
                <Text style={styles.label}>Location</Text>
                <View style={styles.locationRow}>
                    <View style={styles.coordInput}>
                        <Text style={styles.coordLabel}>Latitude</Text>
                        <TextInput
                            style={styles.input}
                            value={latitude}
                            onChangeText={setLatitude}
                            placeholder="Latitude"
                            keyboardType="numeric"
                        />
                    </View>
                    <View style={styles.coordInput}>
                        <Text style={styles.coordLabel}>Longitude</Text>
                        <TextInput
                            style={styles.input}
                            value={longitude}
                            onChangeText={setLongitude}
                            placeholder="Longitude"
                            keyboardType="numeric"
                        />
                    </View>
                </View>
                <TouchableOpacity
                    style={styles.mapButton}
                    onPress={() => setShowMapModal(true)}
                >
                    <Text style={styles.mapButtonText}>📍 Pick Location on Map</Text>
                </TouchableOpacity>
            </View>

            <View style={styles.inputContainer}>
                <Text style={styles.label}>Severity</Text>
                <View style={styles.pickerContainer}>
                    <Picker
                        selectedValue={severity}
                        onValueChange={(itemValue) => setSeverity(itemValue)}
                        style={styles.picker}
                    >
                        <Picker.Item label="low" value="low" />
                        <Picker.Item label="medium" value="medium" />
                        <Picker.Item label="high" value="high" />
                    </Picker>
                </View>
            </View>

            <View style={styles.inputContainer}>
                <Text style={styles.label}>Condition</Text>
                <View style={styles.pickerContainer}>
                    <Picker
                        selectedValue={condition}
                        onValueChange={(itemValue) => setCondition(itemValue)}
                        style={styles.picker}
                    >
                        <Picker.Item label="Minor injury" value="Minor injury" />
                        <Picker.Item label="Fever" value="Fever" />
                        <Picker.Item label="Laceration" value="Laceration" />
                        <Picker.Item label="Fracture" value="Fracture" />
                        <Picker.Item label="Moderate respiratory distress" value="Moderate respiratory distress" />
                        <Picker.Item label="Abdominal pain" value="Abdominal pain" />
                        <Picker.Item label="Heart attack" value="Heart attack" />
                        <Picker.Item label="Major trauma" value="Major trauma" />
                        <Picker.Item label="Stroke" value="Stroke" />
                    </Picker>
                </View>
            </View>

            <View style={styles.buttonContainer}>
                <Button
                    title="Predict Hospital"
                    onPress={handlePredict}
                    color="#007AFF"
                />
            </View>

            {/* Map Modal */}
            <Modal
                visible={showMapModal}
                animationType="slide"
                presentationStyle="fullScreen"
            >
                <SafeAreaView style={styles.modalContainer}>
                    <View style={styles.modalHeader}>
                        <TouchableOpacity
                            style={styles.closeButton}
                            onPress={() => setShowMapModal(false)}
                        >
                            <Text style={styles.closeButtonText}>✕ Close</Text>
                        </TouchableOpacity>
                    </View>
                    <WebView
                        style={styles.webview}
                        source={{ html: getMapHTML() }}
                        onMessage={handleMapMessage}
                        javaScriptEnabled={true}
                        domStorageEnabled={true}
                        originWhitelist={['*']}
                    />
                </SafeAreaView>
            </Modal>
        </SafeAreaView>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        padding: 20,
        backgroundColor: '#fff',
    },
    title: {
        fontSize: 24,
        fontWeight: 'bold',
        textAlign: 'center',
        marginBottom: 20,
        color: '#333',
    },
    inputContainer: {
        marginBottom: 15,
    },
    label: {
        fontSize: 16,
        fontWeight: '600',
        marginBottom: 5,
        color: '#333',
    },
    locationRow: {
        flexDirection: 'row',
        gap: 10,
        marginBottom: 10,
    },
    coordInput: {
        flex: 1,
    },
    coordLabel: {
        fontSize: 14,
        fontWeight: '500',
        marginBottom: 5,
        color: '#666',
    },
    input: {
        borderWidth: 1,
        borderColor: '#ddd',
        borderRadius: 8,
        padding: Platform.OS === 'ios' ? 12 : 8,
        fontSize: 16,
        backgroundColor: '#f9f9f9',
    },
    mapButton: {
        backgroundColor: '#007AFF',
        padding: 12,
        borderRadius: 8,
        alignItems: 'center',
        marginTop: 5,
    },
    mapButtonText: {
        color: '#fff',
        fontSize: 16,
        fontWeight: '600',
    },
    pickerContainer: {
        borderWidth: 1,
        borderColor: '#ddd',
        borderRadius: 8,
        backgroundColor: '#f9f9f9',
        overflow: 'hidden',
    },
    picker: {
        height: Platform.OS === 'ios' ? 200 : 50,
    },
    buttonContainer: {
        marginTop: 20,
        borderRadius: 8,
        overflow: 'hidden',
    },
    modalContainer: {
        flex: 1,
        backgroundColor: '#fff',
    },
    modalHeader: {
        padding: 15,
        backgroundColor: '#f8f8f8',
        borderBottomWidth: 1,
        borderBottomColor: '#ddd',
    },
    closeButton: {
        backgroundColor: '#ff3b30',
        padding: 10,
        borderRadius: 8,
        alignItems: 'center',
        alignSelf: 'flex-end',
    },
    closeButtonText: {
        color: '#fff',
        fontSize: 16,
        fontWeight: '600',
    },
    webview: {
        flex: 1,
    },
    link: {
        marginTop: 15,
        paddingVertical: 15,
    },
});
