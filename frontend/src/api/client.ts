import axios from 'axios';

// Hỗ trợ biến môi trường khi deploy cloud (Render/Vercel) hoặc fallback về /api cho Local/Docker Nginx proxy
export const API_BASE = import.meta.env.VITE_API_URL || '/api';

export const apiClient = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Attach JWT token automatically & handle FormData boundary
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  // Nếu request payload là FormData, xóa Content-Type để browser/Axios tự động gán multipart boundary
  if (config.data instanceof FormData) {
    delete config.headers['Content-Type'];
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
