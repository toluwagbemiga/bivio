import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { notificationApi } from '../services/api/notifications'
import { useToast } from 'vue-toastification'

export const useNotificationStore = defineStore('notifications', () => {
  const notifications = ref([])
  const preferences = ref([])
  const isLoading = ref(false)
  const toast = useToast()

  const unreadNotifications = computed(() => 
    notifications.value.filter(n => !n.is_read)
  )

  const urgentNotifications = computed(() => 
    notifications.value.filter(n => n.priority === 'urgent' && !n.is_read)
  )

  const unreadCount = computed(() => unreadNotifications.value.length)

  const fetchNotifications = async (params = {}) => {
    isLoading.value = true
    try {
      const response = await notificationApi.getNotifications(params)
      notifications.value = response.results || response
      return response
    } catch (error) {
      toast.error('Failed to fetch notifications')
      throw error
    } finally {
      isLoading.value = false
    }
  }

  const fetchPreferences = async () => {
    try {
      const response = await notificationApi.getNotificationPreferences()
      preferences.value = response.results || response
      return response
    } catch (error) {
      toast.error('Failed to fetch notification preferences')
      throw error
    }
  }

  const markAsRead = async (id) => {
    try {
      await notificationApi.markNotificationRead(id)
      const notification = notifications.value.find(n => n.id === id)
      if (notification) {
        notification.is_read = true
        notification.read_at = new Date().toISOString()
      }
      toast.success('Notification marked as read')
    } catch (error) {
      toast.error('Failed to mark notification as read')
      throw error
    }
  }

  const markAllAsRead = async () => {
    try {
      await notificationApi.markAllNotificationsRead()
      notifications.value.forEach(notification => {
        notification.is_read = true
        notification.read_at = new Date().toISOString()
      })
      toast.success('All notifications marked as read')
    } catch (error) {
      toast.error('Failed to mark all notifications as read')
      throw error
    }
  }

  const createNotification = async (notificationData) => {
    try {
      const newNotification = await notificationApi.createNotification(notificationData)
      notifications.value.unshift(newNotification)
      toast.success('Notification created successfully!')
      return newNotification
    } catch (error) {
      toast.error(error.message || 'Failed to create notification')
      throw error
    }
  }

  const updatePreference = async (id, preferenceData) => {
    try {
      const updatedPreference = await notificationApi.updateNotificationPreference(id, preferenceData)
      const index = preferences.value.findIndex(p => p.id === id)
      if (index !== -1) {
        preferences.value[index] = updatedPreference
      }
      toast.success('Notification preference updated!')
      return updatedPreference
    } catch (error) {
      toast.error(error.message || 'Failed to update preference')
      throw error
    }
  }

  const toggleChannel = async (id, channel) => {
    try {
      const updatedPreference = await notificationApi.toggleChannel(id, { channel })
      const index = preferences.value.findIndex(p => p.id === id)
      if (index !== -1) {
        preferences.value[index] = updatedPreference
      }
      return updatedPreference
    } catch (error) {
      toast.error('Failed to toggle notification channel')
      throw error
    }
  }

  return {
    notifications,
    preferences,
    isLoading,
    unreadNotifications,
    urgentNotifications,
    unreadCount,
    fetchNotifications,
    fetchPreferences,
    markAsRead,
    markAllAsRead,
    createNotification,
    updatePreference,
    toggleChannel
  }
})
