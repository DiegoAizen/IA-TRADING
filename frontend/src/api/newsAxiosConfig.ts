// frontend/src/api/newsAxiosConfig.ts - NUEVO ARCHIVO
import axios from 'axios';

// ✅ ESPECÍFICO PARA NOTICIAS (con /api en baseURL)
const newsApi = axios.create({
  baseURL: 'http://localhost:8000/api', // ← CON /api aquí
  timeout: 10000,
});

// Interceptor para agregar token automáticamente
newsApi.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
      console.log('🔐 Token añadido a request de noticias');
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Interceptor para manejar errores de autenticación
newsApi.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('❌ Error en noticias:', error.response?.status);
    
    if (error.response?.status === 401 || error.response?.status === 403) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('user_data');
      localStorage.removeItem('token_expires');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default newsApi;