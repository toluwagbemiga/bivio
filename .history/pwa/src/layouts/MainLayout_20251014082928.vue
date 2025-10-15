<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <header class="bg-white shadow-sm border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-16">
          <!-- Logo -->
          <div class="flex items-center">
            <img src="logo.svg" alt="Bivio" class="h-8 w-8" />
            <span class="ml-2 text-xl font-bold text-gray-900">Bivio POS</span>
          </div>
          
          <!-- User menu -->
          <div class="flex items-center space-x-4">
            <!-- Notifications -->
            <button 
              @click="toggleNotifications"
              class="relative p-2 text-gray-400 hover:text-gray-500"
            >
              <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
              </svg>
              <span v-if="unreadNotifications > 0" class="absolute -top-1 -right-1 h-4 w-4 bg-red-500 text-white text-xs rounded-full flex items-center justify-center">
                {{ unreadNotifications }}
              </span>
            </button>
            
            <!-- Offline indicator -->
            <div v-if="!isOnline" class="flex items-center text-orange-600">
              <svg class="h-4 w-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
              <span class="text-sm">Offline</span>
            </div>
            
            <!-- User dropdown -->
            <div class="relative">
              <button 
                @click="toggleUserMenu"
                class="flex items-center space-x-2 text-sm text-gray-700 hover:text-gray-900"
              >
                <div class="h-8 w-8 bg-blue-600 rounded-full flex items-center justify-center text-white font-medium">
                  {{ userInitials }}
                </div>
                <span>{{ user?.full_name || 'User' }}</span>
                <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                </svg>
              </button>
              
              <!-- Dropdown menu -->
              <div v-if="showUserMenu" class="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg py-1 z-50">
                <a href="#" class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">Profile</a>
                <a href="#" class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">Settings</a>
                <hr class="my-1">
                <button @click="logout" class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">
                  Logout
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </header>

    <div class="flex">
      <!-- Sidebar -->
      <aside class="w-64 bg-white shadow-sm min-h-screen">
        <nav class="mt-5 px-2">
          <div class="space-y-1">
            <router-link
              v-for="item in navigation"
              :key="item.name"
              :to="item.href"
              :class="[
                $route.path === item.href
                  ? 'bg-blue-100 text-blue-900'
                  : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900',
                'group flex items-center px-2 py-2 text-sm font-medium rounded-md'
              ]"
            >
              <component :is="item.icon" class="mr-3 h-5 w-5" />
              {{ item.name }}
            </router-link>
          </div>
        </nav>
      </aside>

      <!-- Main content -->
      <main class="flex-1 p-6">
        <router-view />
      </main>
    </div>

    <!-- Notifications panel -->
    <div v-if="showNotifications" class="fixed inset-0 z-50 overflow-hidden">
      <div class="absolute inset-0 bg-black bg-opacity-25" @click="toggleNotifications"></div>
      <div class="absolute right-0 top-0 h-full w-96 bg-white shadow-xl">
        <div class="p-6">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-medium text-gray-900">Notifications</h3>
            <button @click="toggleNotifications" class="text-gray-400 hover:text-gray-500">
              <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          <div class="space-y-3">
            <div v-for="notification in notifications" :key="notification.id" class="p-3 bg-gray-50 rounded-lg">
              <div class="flex items-start justify-between">
                <div>
                  <p class="text-sm font-medium text-gray-900">{{ notification.title }}</p>
                  <p class="text-sm text-gray-600">{{ notification.message }}</p>
                </div>
                <span v-if="!notification.is_read" class="h-2 w-2 bg-blue-600 rounded-full"></span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useNotificationStore } from '../stores/notifications'
import { useOfflineStore } from '../stores/offline'

const router = useRouter()
const authStore = useAuthStore()
const notificationStore = useNotificationStore()
const offlineStore = useOfflineStore()

const showUserMenu = ref(false)
const showNotifications = ref(false)

const user = computed(() => authStore.user)
const notifications = computed(() => notificationStore.notifications)
const unreadNotifications = computed(() => notificationStore.unreadCount)
const isOnline = computed(() => offlineStore.isOnline)

const userInitials = computed(() => {
  if (!user.value) return 'U'
  const name = user.value.full_name || user.value.email
  return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
})

const navigation = [
  { name: 'Dashboard', href: '/', icon: 'DashboardIcon' },
  { name: 'Inventory', href: '/inventory', icon: 'InventoryIcon' },
  { name: 'Transactions', href: '/transactions', icon: 'TransactionIcon' },
  { name: 'Loans', href: '/loans', icon: 'LoanIcon' },
  { name: 'Savings', href: '/savings', icon: 'SavingsIcon' },
  { name: 'Analytics', href: '/analytics', icon: 'AnalyticsIcon' },
  { name: 'Settings', href: '/settings', icon: 'SettingsIcon' }
]

const toggleUserMenu = () => {
  showUserMenu.value = !showUserMenu.value
}

const toggleNotifications = () => {
  showNotifications.value = !showNotifications.value
}

const logout = async () => {
  await authStore.logout()
  router.push('/login')
}

// Close menus when clicking outside
const handleClickOutside = (event) => {
  if (!event.target.closest('.relative')) {
    showUserMenu.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
  notificationStore.fetchNotifications()
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>
