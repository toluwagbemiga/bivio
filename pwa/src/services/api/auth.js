import api from './base'

export const authApi = {
  // Authentication
  login: (credentials) => api.post('/users/login/', credentials),
  register: (userData) => api.post('/users/register/', userData),
  logout: () => api.post('/users/logout/'),
  
  // Profile management
  getProfile: () => api.get('/users/profile/'),
  updateProfile: (profileData) => api.put('/users/profile/', profileData),
  
  // User management (admin only)
  getUsers: (params) => api.get('/users/users/', { params }),
  getUser: (id) => api.get(`/users/users/${id}/`),
  updateUser: (id, userData) => api.put(`/users/users/${id}/`, userData),
  verifyUser: (id, verificationData) => api.post(`/users/users/${id}/verify/`, verificationData),
  
  // Business profile
  getBusinessProfile: () => api.get('/users/business-profiles/'),
  createBusinessProfile: (profileData) => api.post('/users/business-profiles/', profileData),
  updateBusinessProfile: (id, profileData) => api.put(`/users/business-profiles/${id}/`, profileData),
  verifyBusinessProfile: (id, verificationData) => api.post(`/users/business-profiles/${id}/verify/`, verificationData),
  
  // Guarantors
  getGuarantors: () => api.get('/users/guarantors/'),
  createGuarantor: (guarantorData) => api.post('/users/guarantors/', guarantorData),
  updateGuarantor: (id, guarantorData) => api.put(`/users/guarantors/${id}/`, guarantorData),
  deleteGuarantor: (id) => api.delete(`/users/guarantors/${id}/`),
  
  // Dashboard stats
  getDashboardStats: (id) => api.get(`/users/users/${id}/dashboard_stats/`)
}
