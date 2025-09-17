import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL;

// Create Axios instance
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Attach token to every request if available
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle global errors (optional)
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API error:', error);
    return Promise.reject(error);
  }
);

// Auth endpoints
export const loginUser = (email, password) =>
  api.post('/auth/login', { email, password });

export const registerUser = (email, password) =>
  api.post('/auth/register', { email, password });

export const fetchUserProfile = () =>
  api.get('/auth/me');

// Resume endpoints
export const uploadResume = (resumeFile, jobDescription) => {
  const formData = new FormData();
  formData.append('resume', resumeFile);
  formData.append('jobDescription', jobDescription);

  return api.post('/resume/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
};

export const fetchResumeHistory = () =>
  api.get('/resume/history');

export const downloadPDFReport = (analysis) =>
  api.post('/resume/download-pdf', { analysis }, { responseType: 'blob' });

export default api; 
