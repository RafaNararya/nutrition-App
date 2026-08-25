import axios from 'axios';

// Pointing to your FastAPI server running on port 8000
const API_BASE_URL = 'http://localhost:8000';

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

export const registerUser = (userData) => api.post('/users/', userData);

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

export default api;