import axios from 'axios';

// Grab URL from Vite env or fallback to railway domain
let rawUrl = import.meta.env.VITE_API_URL || 'https://nutrition-app-production-b8b1.up.railway.app';

// Ensure it ALWAYS uses https:// and has no trailing slash
if (rawUrl.startsWith('http://') && !rawUrl.includes('localhost')) {
  rawUrl = rawUrl.replace('http://', 'https://');
}

const API_BASE_URL = rawUrl.replace(/\/$/, '');

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});
// Helper functions for your OpenAPI routes
export const getStatus = () => api.get('/status');

export const searchFood = (query) => {
  // Send parameter name as 'query' instead of 'q'
  return api.get('/search', { params: { query } });
};

export const registerUser = (userData) => api.post('/users', userData);

export const updateUserProfile = (userId, profileData) =>
  api.put(`/users/profile/${userId}`, profileData);

export const recordMeal = (mealData) => api.post('/meals/', mealData);

export const getUserLogs = (userId) => api.get(`/meals/${userId}`);

export const getUserSummary = (userId) => api.get(`/meals/summary/${userId}`);

export const removeMealLog = (userId, mealLogId) =>
  api.delete(`/meals/${userId}/log/${mealLogId}`);

export const getFoodSubstitutions = (foodId) =>
  api.get(`/recommendations/substitute/${foodId}`);

export const getDeficitRecommendations = (userId) =>
  api.get(`/recommendations/deficit/${userId}`);

export const loginUser = async (credentials) => {
  // credentials = { username, password }
  return await api.post('/users/login', credentials);
};

export const getMealHistory = (userId) => api.get(`/meals/history/${userId}`);

export default api;