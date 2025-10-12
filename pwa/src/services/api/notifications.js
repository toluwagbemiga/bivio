import api from './base'

export const notificationApi = {
  // Notifications
  getNotifications: (params) => api.get('/notifications/notifications/', { params }),
  getNotification: (id) => api.get(`/notifications/notifications/${id}/`),
  createNotification: (notificationData) => api.post('/notifications/notifications/', notificationData),
  updateNotification: (id, notificationData) => api.put(`/notifications/notifications/${id}/`, notificationData),
  deleteNotification: (id) => api.delete(`/notifications/notifications/${id}/`),
  getUnreadNotifications: () => api.get('/notifications/notifications/unread/'),
  getUrgentNotifications: () => api.get('/notifications/notifications/urgent/'),
  getNotificationsByType: (type) => api.get('/notifications/notifications/by_type/', { params: { type } }),
  markNotificationRead: (id) => api.post(`/notifications/notifications/${id}/mark_read/`),
  markAllNotificationsRead: () => api.post('/notifications/notifications/mark_all_read/'),
  getDashboardStats: () => api.get('/notifications/notifications/dashboard_stats/'),
  createSystemNotification: (notificationData) => api.post('/notifications/notifications/create_system_notification/', notificationData),
  cleanupExpiredNotifications: () => api.post('/notifications/notifications/cleanup_expired/'),
  
  // Notification Preferences
  getNotificationPreferences: (params) => api.get('/notifications/preferences/', { params }),
  getNotificationPreference: (id) => api.get(`/notifications/preferences/${id}/`),
  createNotificationPreference: (preferenceData) => api.post('/notifications/preferences/', preferenceData),
  updateNotificationPreference: (id, preferenceData) => api.put(`/notifications/preferences/${id}/`, preferenceData),
  deleteNotificationPreference: (id) => api.delete(`/notifications/preferences/${id}/`),
  getActivePreferences: () => api.get('/notifications/preferences/active/'),
  bulkUpdatePreferences: (bulkData) => api.post('/notifications/preferences/bulk_update/', bulkData),
  getPreferencesSummary: () => api.get('/notifications/preferences/summary/'),
  toggleChannel: (id, channelData) => api.post(`/notifications/preferences/${id}/toggle_channel/`, channelData)
}
