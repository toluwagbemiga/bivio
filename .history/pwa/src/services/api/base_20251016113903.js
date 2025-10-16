import axios from 'axios'
import { useToast } from 'vue-toastification'

// Create axios instance
const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Token ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    const toast = useToast()
    
    if (error.response) {
      const { status, data } = error.response
      
      switch (status) {
        case 401:
          toast.error('Authentication required')
          localStorage.removeItem('auth_token')
          window.location.href = '/login'
          break
        case 403:
          toast.error('Permission denied')
          break
        case 404:
          toast.error('Resource not found')
          break
        case 422:
          toast.error(data.message || 'Validation error')
          break
        case 500:
          toast.error('Server error occurred')
          break
        default:
          toast.error(data.message || 'An error occurred')
      }
    } else if (error.request) {
      toast.error('Network error - please check your connection')
    } else {
      toast.error('An unexpected error occurred')
    }
    
    return Promise.reject(error)
  }
)

export default api
