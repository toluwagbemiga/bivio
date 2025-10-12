import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useToast } from 'vue-toastification'

export const useOfflineStore = defineStore('offline', () => {
  const isOnline = ref(navigator.onLine)
  const isInitialized = ref(false)
  const toast = useToast()

  const initialize = async () => {
    // Listen for online/offline events
    window.addEventListener('online', handleOnline)
    window.addEventListener('offline', handleOffline)
    
    isInitialized.value = true
  }

  const handleOnline = () => {
    isOnline.value = true
    toast.success('Connection restored!')
  }

  const handleOffline = () => {
    isOnline.value = false
    toast.warning('You are now offline. Some features may be limited.')
  }

  const cleanup = () => {
    window.removeEventListener('online', handleOnline)
    window.removeEventListener('offline', handleOffline)
  }

  return {
    isOnline,
    isInitialized,
    initialize,
    cleanup
  }
})
