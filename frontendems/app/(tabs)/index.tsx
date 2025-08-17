import { StyleSheet, TouchableOpacity, Alert, View, Text, Button, Dimensions } from 'react-native';
import { useAuth } from '../../contexts/AuthContext';
import { WebView } from 'react-native-webview';
import { useEffect, useState, useMemo } from 'react';
import { useLocalSearchParams } from 'expo-router';

//since we're not going to use gitignore for simplicity:
// use this API KEY: 
const ORS_KEY = "eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6IjhlYmE3NGQ4NzRlYTRlMmQ4ZDEyYjQxMTk1MGIzNmIyIiwiaCI6Im11cm11cjY0In0=";



// #info: Summary of ORS + Leaflet works here.
// 1: on Mount: useEffect calls fetchRoute()
//      where: fetchRoute builds a body [long,lat] => to be send 
//      to API of openRouteService. read docu above
//      
// 2: after fetching: setRouteCoordinates() with the returned coordinates


// 3: now we have routeCoordinates: we will use this to plot "POLYLINE" in leaflet

// 4: [userCoordinates, hospitalCoordinates, routeCoordinates].
// 4: [marker for user, marker for hospital, the route line.]

// 5: create map HTML content with Leaflet. that's it. (BUGGED ANG NATIVE)

// #end-info



export default function HomeScreen() {
  const params = useLocalSearchParams();
  
  // Check if we have prediction data from the predict screen
  const hasPredictionData = params.prediction === 'true';
  
  // IF predictionData from predict.tsx exist, USE IT. else otherwise use default coordinates
  const [userCoords, setUserCoords] = useState({ 
    latitude: hasPredictionData ? parseFloat(params.userLat as string) : 14.65, 
    longitude: hasPredictionData ? parseFloat(params.userLon as string) : 121.10 
  });
  
  const [predictedHospitalCoords, setPredictedHospitalCoords] = useState({ 
    latitude: hasPredictionData ? parseFloat(params.hospitalLat as string) : 14.6361025, 
    longitude: hasPredictionData ? parseFloat(params.hospitalLon as string) : 121.0984445 
  });


  // to be set on fetchRoute()...
  const [routeCoordinates, setRouteCoordinates] = useState<Array<[number, number]>>([]);
  const [isLoadingRoute, setIsLoadingRoute] = useState(false);
  const [lastFetchTime, setLastFetchTime] = useState(0);
  





  // use the additional prediction info for display. sayang
  const [predictionInfo, setPredictionInfo] = useState<{
    hospitalName?: string;
    hospitalLevel?: string;
    distance?: string;
    totalTime?: string;
  }>({});






  // Update prediction info when params change
  useEffect(() => {
    if (hasPredictionData) {
      setPredictionInfo({
        hospitalName: params.hospitalName as string,
        hospitalLevel: params.hospitalLevel as string,
        distance: params.distance as string,
        totalTime: params.totalTime as string,
      });
      
      // Update coordinates from params
      setUserCoords({
        latitude: parseFloat(params.userLat as string),
        longitude: parseFloat(params.userLon as string)
      });
      
      setPredictedHospitalCoords({
        latitude: parseFloat(params.hospitalLat as string),
        longitude: parseFloat(params.hospitalLon as string)
      });
    }
  }, [params]);











  // #info: GOAL?? get the routeCoordinates (THE LINE IN MAP). thats all.
  async function fetchRoute() {


    /*
    pseudocode:
        USE the coordinates of userCoords && predictedHospitalCoords.
        send it as (BODY) request to that api...

        The openrouteservice will automatically compute the route.

        for example openrouteservice returns 66 coordinates. the leaflet will map it. 
        
        #thats all

    */


    const currentTime = Date.now();
    // #error: 429 -> too many request. SOLUTION: debounce + memoization.
    if (currentTime - lastFetchTime < 2000) {
      console.log('Rate limiting: skipping request (too frequent)');
      return;
    }
    
    if (isLoadingRoute) {
      console.log('Already loading route, skipping request');
      return;
    }

    setIsLoadingRoute(true);
    setLastFetchTime(currentTime);

    try {


      //call api PREDICT after filling the PREDICT FORM (predict.tsx) to get predictedHospitalCoords (which will be used as polyline line).


      const body = {
        coordinates: [
          [userCoords.longitude, userCoords.latitude], // [lon, lat] user
          [predictedHospitalCoords.longitude, predictedHospitalCoords.latitude] // [lon, lat] hospital
        ]
      };

      const res = await fetch('https://api.openrouteservice.org/v2/directions/driving-car/geojson', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': ORS_KEY
        },
        body: JSON.stringify(body)
      });

      if (!res.ok) {
        const errorText = await res.text();
        console.error('ORS error:', errorText);
        
        if (res.status === 429) {
          Alert.alert(
            'Rate Limit Exceeded', 
            'Too many route requests. Please wait a moment before trying again.'
          );
        } else {
          Alert.alert('Routing Error', `Failed to get route: ${res.status}`);
        }
        // #r
        return;
      }

      const geo = await res.json();
      console.log(geo)


      // ai generated idk. basta
      if (geo.features && geo.features[0] && geo.features[0].geometry) {
        
        const coordinates = geo.features[0].geometry.coordinates; 


        setRouteCoordinates(coordinates); //this are [lon, lat] pairs

        //#note: THESE ARE LARGE NUMBERS. why? this is the step by step route.
        //#note: basically the leaflet will loop this. kinda
        console.log('Route fetched with', coordinates.length, 'points');
      }
    } catch (error) {
      console.error('Route fetch error:', error);
      Alert.alert('Error', 'Failed to fetch route');
    } finally {
      setIsLoadingRoute(false);
    }
  }









  // if read top to bottom, at this point we now have routeCoordinates to polyline the map... aka the direction of line










  // #warning: LEARN MEMOIZED FOR THIS PART

  // memoized to prevent error 429. (too many request)
  const mapHTML = useMemo(() => {
    const routeCoordinatesString = JSON.stringify(routeCoordinates.map(coord => [coord[1], coord[0]])); // Convert to [lat, lon] for Leaflet
    console.log('Generating map HTML with', routeCoordinates.length, 'route points');

    return `
    <!DOCTYPE html>
    <html>


    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
        <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
        <style>
            body { margin: 0; padding: 0; }
            #map { height: 100vh; width: 100vw; }
        </style>
    </head>


    <body>
        <div id="map"></div>
        <script>
            const map = L.map('map').setView([${userCoords.latitude}, ${userCoords.longitude}], 13);
            
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '© OpenStreetMap contributors'
            }).addTo(map);
            
            // User marker
            L.marker([${userCoords.latitude}, ${userCoords.longitude}])
                .addTo(map)
                .bindPopup('Your Location')
                .openPopup();
            
            // Hospital marker
            L.marker([${predictedHospitalCoords.latitude}, ${predictedHospitalCoords.longitude}])
                .addTo(map)
                .bindPopup('Hospital');
            
            // Route polyline
            const routeCoords = ${routeCoordinatesString};
            if (routeCoords.length > 0) {
                L.polyline(routeCoords, {color: '#ff0000ff', weight: 4}).addTo(map);
                
                // Fit map to show all points
                const group = new L.featureGroup([
                    L.marker([${userCoords.latitude}, ${userCoords.longitude}]),
                    L.marker([${predictedHospitalCoords.latitude}, ${predictedHospitalCoords.longitude}]),
                    L.polyline(routeCoords)
                ]);
                map.fitBounds(group.getBounds().pad(0.1));
            }
        </script>
    </body>
    </html>
    `;
  }, [userCoords.latitude, userCoords.longitude, predictedHospitalCoords.latitude, predictedHospitalCoords.longitude, routeCoordinates]);
  // Only fetch route on initial load or when coordinates change significantly
  
  
  
  useEffect(() => {
    // ai generated logic: to avoid error 429 (too much requests)
    const hasSignificantChange = 
      routeCoordinates.length === 0 || 
      Math.abs(userCoords.latitude - (routeCoordinates[0]?.[1] || 0)) > 0.001 ||
      Math.abs(userCoords.longitude - (routeCoordinates[0]?.[0] || 0)) > 0.001 ||
      Math.abs(predictedHospitalCoords.latitude - (routeCoordinates[routeCoordinates.length - 1]?.[1] || 0)) > 0.001 ||
      Math.abs(predictedHospitalCoords.longitude - (routeCoordinates[routeCoordinates.length - 1]?.[0] || 0)) > 0.001;

    if (hasSignificantChange) {
      const timeoutId = setTimeout(() => {
        console.log('Triggering route fetch due to coordinate change');
        fetchRoute();
      }, 1000); // Wait 1 second after coordinates change before fetching route

      return () => clearTimeout(timeoutId);
    }
  }, [userCoords.latitude, userCoords.longitude, predictedHospitalCoords.latitude, predictedHospitalCoords.longitude]);

  return (
    <View style={{ flex: 1 }}>
      <WebView
        style={{ flex: 1 }}
        source={{ html: mapHTML }}
        javaScriptEnabled={true}
        domStorageEnabled={true}
      />

      {/* the additional info. from /predict */}
      {hasPredictionData && (
        <View style={styles.predictionInfo}>
          <Text style={styles.predictionTitle}>🏥 Predicted Hospital</Text>
          <Text style={styles.predictionText}>
            <Text style={styles.predictionLabel}>Hospital: </Text>
            {predictionInfo.hospitalName}
          </Text>
          <Text style={styles.predictionText}>
            <Text style={styles.predictionLabel}>Level: </Text>
            {predictionInfo.hospitalLevel}
          </Text>
          <Text style={styles.predictionText}>
            <Text style={styles.predictionLabel}>Distance: </Text>
            {parseFloat(predictionInfo.distance || '0').toFixed(2)} km
          </Text>
          <Text style={styles.predictionText}>
            <Text style={styles.predictionLabel}>Total Time: </Text>
            {parseFloat(predictionInfo.totalTime || '0').toFixed(1)} minutes
          </Text>
        </View>
      )}

      <View style={styles.buttonContainer}>
        <Button 
          title={isLoadingRoute ? "Loading Route..." : "Recompute Route"} 
          onPress={fetchRoute}
          disabled={isLoadingRoute}
        />
      </View>
    </View>
  );
}
















const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16,
  },
  header: {
    alignItems: 'center',
    marginBottom: 32,
    marginTop: 16,
    paddingBottom: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#0a7ea4',
  },
  subtitle: {
    fontSize: 18,
    color: '#666',
    marginTop: 8,
  },
  roleText: {
    fontSize: 14,
    color: '#666',
    marginTop: 4,
  },
  content: {
    flex: 1,
    gap: 24,
  },
  dashboardTitle: {
    fontSize: 20,
    fontWeight: '600',
    color: '#333',
  },
  description: {
    fontSize: 16,
    color: '#666',
    lineHeight: 24,
  },
  statsContainer: {
    flexDirection: 'row',
    gap: 16,
    marginVertical: 16,
  },
  statCard: {
    flex: 1,
    backgroundColor: '#f5f5f5',
    padding: 16,
    borderRadius: 8,
    alignItems: 'center',
    gap: 8,
  },
  statLabel: {
    fontSize: 14,
    fontWeight: '600',
    color: '#666',
  },
  statNumber: {
    color: '#0a7ea4',
    fontSize: 24,
    fontWeight: 'bold',
  },
  logoutButton: {
    backgroundColor: '#dc3545',
    borderRadius: 8,
    padding: 16,
    alignItems: 'center',
    marginTop: 'auto',
    marginBottom: 16,
  },
  logoutButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  markerContainer: {
    alignItems: 'center',
  },
  marker: {
    width: 12,
    height: 12,
    borderRadius: 6,
    borderWidth: 2,
    borderColor: '#fff',
  },
  markerText: {
    fontSize: 10,
    fontWeight: 'bold',
    color: '#333',
    marginTop: 2,
    backgroundColor: 'rgba(255,255,255,0.8)',
    paddingHorizontal: 4,
    paddingVertical: 1,
    borderRadius: 3,
  },
  buttonContainer: {
    position: 'absolute',
    bottom: 20,
    left: 20,
    right: 20,
    backgroundColor: 'rgba(255,255,255,0.9)',
    borderRadius: 8,
    padding: 10,
  },
  predictionInfo: {
    position: 'absolute',
    top: 50,
    left: 20,
    right: 20,
    backgroundColor: 'rgba(255,255,255,0.95)',
    borderRadius: 12,
    padding: 15,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
    elevation: 5,
  },
  predictionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#007AFF',
    marginBottom: 10,
    textAlign: 'center',
  },
  predictionText: {
    fontSize: 14,
    color: '#333',
    marginBottom: 5,
  },
  predictionLabel: {
    fontWeight: '600',
    color: '#666',
  },
});
