import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';


//#error: if axios error: 

// go to terminal
// do ipconfig
// get ipv4 address
// change the localhost to 192.168.*.**.. keep 8000, depends gets niyo na yan

//#end-error: if axios error: 

const BASE_URL = 'http://192.168.1.11:8000'; 

const apiClient = axios.create({
  baseURL: BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});



// #warning: comment temporarily, this is just JWT if mag totoken tayo.
// apiClient.interceptors.request.use(
//   async (config) => {
//     try {
//       const token = await AsyncStorage.getItem('authToken');
//       if (token) {
//         config.headers.Authorization = `Bearer ${token}`;
//       }
//     } catch (error) {
//       console.error('Error getting auth token:', error);
//     }
//     return config;
//   },
//   (error) => {
//     return Promise.reject(error);
//   }
// );
// #end-warning:


// API fastApi interceptor to handle errors: depending to what we recieve. 
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid, clear storage and redirect to login
      // await AsyncStorage.removeItem('authToken');
      // await AsyncStorage.removeItem('userData');
      // You can add navigation logic here if needed
    }
    return Promise.reject(error);
  }
);


//D.O.T interface
export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
  name: string;
  role: 'dispatcher' | 'ems_personnel' | 'admin';
}

export interface User {
  id: string;
  email: string;
  name: string;
  role: string;
}

export interface AuthResponse {
  token: string;
  user: User;
}

export interface Emergency {
  id: string;
  patientName: string;
  location: string;
  coordinates: {
    latitude: number;
    longitude: number;
  };
  severity: 'low' | 'medium' | 'high' | 'critical';
  condition: string;
  status: 'pending' | 'assigned' | 'en_route' | 'arrived' | 'completed';
  ambulanceId?: string;
  hospitalId?: string;
  createdAt: string;
  updatedAt: string;
}


export interface Hospital {
  id: string;
  name: string;
  address: string;
  coordinates: {
    latitude: number;
    longitude: number;
  };
  capacity: number;
  availableBeds: number;
  specialties: string[];
}



// PREDICTION INTERFACE


// {
//   "latitude": 14.65,
//   "longitude": 121.10,
//   "severity": "medium",
//   "condition": "Fracture"
// }

// Input:
export interface PredictInput {
  latitude: number;
  longitude: number;
  // limited set in UI but backend may accept string; keep union for safety
  severity: 'low' | 'medium' | 'high' | 'critical' | string;
  condition: string;
}
// END-INPUT:



export interface HospitalPrediction {
  id: number;
  name: string;
  level: string;
  // [lat, lon]
  coords: [number, number];
  distance_km: number;
}

export interface EMSBasePrediction {
  base_id: number;
  base_name: string;
  // [lat, lon]
  coords: [number, number];
  distance_km: number;
  time_min: number;
  is_road_distance: boolean;
}

export interface TimeComponents {
  dispatch_time: number;
  time_to_patient: number;
  on_scene_time: number;
  time_to_hospital: number;
  handover_time: number;
  total_time: number;
}



// RESPONSE:
// {
//     "hospital": {
//         "id": 1,
//         "name": "Amang Rodriguez Memorial Medical Center",
//         "level": "3",
//         "coords": [
//             14.6361025,
//             121.0984445
//         ],
//         "distance_km": 1.5543661172970407
//     },
//     "ems_base": {
//         "base_id": 166,
//         "base_name": "166 Base - CHO Office, Barangay Sto.niño",
//         "coords": [
//             14.6399746,
//             121.0965973
//         ],
//         "distance_km": 1.1733404026496732,
//         "time_min": 1.7600106039745098,
//         "is_road_distance": false
//     },
//     "time_components": {
//         "dispatch_time": 2.0,
//         "time_to_patient": 1.7600106039745098,
//         "on_scene_time": 10.0,
//         "time_to_hospital": 0.2307999682325173,
//         "handover_time": 5.0,
//         "total_time": 18.990810572207028
//     },
//     "is_fallback_calculation": false
// }
export interface PredictResponse {
  hospital: HospitalPrediction;
  ems_base: EMSBasePrediction;
  time_components: TimeComponents;
  is_fallback_calculation: boolean;
}


export const predict = async (input: PredictInput): Promise<PredictResponse> => {
  try {
    const response = await apiClient.post('/predict', input);
    return response.data as PredictResponse;
  } catch (error) {
    console.error('Predict API error:', error);
    throw error;
  }
};

export const getAllMaps = async () => {
  try {
    const response = await apiClient.get('/get-all-maps');
    return response.data;
  } catch (error) {
    console.error('Get all maps error:', error);
    throw error;
  }
};


































// WALA ITOOOOOO WALA ITOOOOOO
// WALA ITOOOOOO WALA ITOOOOOO

// WALA ITOOOOOO WALA ITOOOOOO

// WALA ITOOOOOO WALA ITOOOOOO

// WALA ITOOOOOO WALA ITOOOOOO

// WALA ITOOOOOO WALA ITOOOOOO

// WALA ITOOOOOO WALA ITOOOOOO
// WALA ITOOOOOO WALA ITOOOOOO

// WALA ITOOOOOO WALA ITOOOOOO

// WALA ITOOOOOO WALA ITOOOOOO
// WALA ITOOOOOO WALA ITOOOOOO
// WALA ITOOOOOO WALA ITOOOOOO

// WALA ITOOOOOO WALA ITOOOOOO





// #error: NVM THIS LINES.... boiler plate lang
// Authentication API calls
export const login = async (credentials: LoginCredentials) => {
  try {
    const response = await apiClient.post('/auth/login', credentials);
    return response.data;
  } catch (error) {
    console.error('Login error:', error);
    throw error;
  }
};

export const register = async (userData: RegisterData) => {
  try {
    const response = await apiClient.post('/auth/register', userData);
    return response.data;
  } catch (error) {
    console.error('Register error:', error);
    throw error;
  }
};

export const getProfile = async () => {
  try {
    const response = await apiClient.get('/auth/profile');
    return response.data;
  } catch (error) {
    console.error('Get profile error:', error);
    throw error;
  }
};

export const logout = async () => {
  try {
    await apiClient.post('/auth/logout');
  } catch (error) {
    console.error('Logout error:', error);
    throw error;
  }
};

export const refreshToken = async () => {
  try {
    const response = await apiClient.post('/auth/refresh');
    return response.data;
  } catch (error) {
    console.error('Refresh token error:', error);
    throw error;
  }
};
// #end-error

export default apiClient;
