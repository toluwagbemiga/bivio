<template>
  <div id="app" class="min-h-screen bg-gray-50">
    <router-view />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useAuthStore } from './stores/auth'
import { useOfflineStore } from './stores/offline'

const authStore = useAuthStore()
const offlineStore = useOfflineStore()

onMounted(async () => {
  // Initialize auth state
  await authStore.initialize()
  
  // Initialize offline support
  await offlineStore.initialize()
  
  // Register service worker
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/sw.js')
      .then(registration => {
        console.log('SW registered: ', registration)
      })
      .catch(registrationError => {
        console.log('SW registration failed: ', registrationError)
      })
  }
})
</script>
