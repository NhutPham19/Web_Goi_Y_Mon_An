import axios from 'axios';

// Vite proxy forwards /api to http://localhost:5000/api
export const API_BASE = '/api';

export const apiClient = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Attach JWT token automatically
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle global response
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Optional: clear expired token
      // localStorage.removeItem('token');
    }
    return Promise.reject(error);
  }
);
