import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '../services/api/auth'
import { useToast } from 'vue-toastification'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('auth_token'))
  const isLoading = ref(false)
  const toast = useToast()

  const isAuthenticated = computed(() => !!token.value && !!user.value)

  const initialize = async () => {
    if (token.value) {
      try {
        const userData = await authApi.getProfile()
        user.value = userData
      } catch (error) {
        console.error('Failed to initialize auth:', error)
        logout()
      }
    }
  }

  const login = async (credentials) => {
    isLoading.value = true
    try {
      const response = await authApi.login(credentials)
      token.value = response.token
      user.value = response.user
      localStorage.setItem('auth_token', response.token)
      toast.success('Login successful!')
      return response
    } catch (error) {
      toast.error(error.message || 'Login failed')
      throw error
    } finally {
      isLoading.value = false
    }
  }

  const register = async (userData) => {
    isLoading.value = true
    try {
      const response = await authApi.register(userData)
      token.value = response.token
      user.value = response.user
      localStorage.setItem('auth_token', response.token)
      toast.success('Registration successful!')
      return response
    } catch (error) {
      toast.error(error.message || 'Registration failed')
      throw error
    } finally {
      isLoading.value = false
    }
  }

  const logout = async () => {
    try {
      await authApi.logout()
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      token.value = null
      user.value = null
      localStorage.removeItem('auth_token')
    }
  }

  const updateProfile = async (profileData) => {
    try {
      const updatedUser = await authApi.updateProfile(profileData)
      user.value = updatedUser
      toast.success('Profile updated successfully!')
      return updatedUser
    } catch (error) {
      toast.error(error.message || 'Profile update failed')
      throw error
    }
  }

  return {
    user,
    token,
    isLoading,
    isAuthenticated,
    initialize,
    login,
    register,
    logout,
    updateProfile
  }
})
