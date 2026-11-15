import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000',
});

// Har request ke saath token bhejne ke liye interceptor
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default api;