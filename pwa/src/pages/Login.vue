<template>
  <div>
    <div class="mb-6">
      <h2 class="text-2xl font-bold text-gray-900">Sign in to your account</h2>
      <p class="mt-2 text-sm text-gray-600">
        Or
        <button @click="showRegister = true" class="font-medium text-blue-600 hover:text-blue-500">
          create a new account
        </button>
      </p>
    </div>

    <!-- Login Form -->
    <div v-if="!showRegister">
      <form @submit.prevent="handleLogin" class="space-y-6">
        <div>
          <label for="email" class="label">Email address</label>
          <input
            id="email"
            v-model="loginForm.email"
            type="email"
            required
            class="input"
            placeholder="Enter your email"
          />
        </div>

        <div>
          <label for="password" class="label">Password</label>
          <input
            id="password"
            v-model="loginForm.password"
            type="password"
            required
            class="input"
            placeholder="Enter your password"
          />
        </div>

        <div class="flex items-center justify-between">
          <div class="flex items-center">
            <input
              id="remember-me"
              v-model="loginForm.remember"
              type="checkbox"
              class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <label for="remember-me" class="ml-2 block text-sm text-gray-900">
              Remember me
            </label>
          </div>

          <div class="text-sm">
            <a href="#" class="font-medium text-blue-600 hover:text-blue-500">
              Forgot your password?
            </a>
          </div>
        </div>

        <div>
          <button
            type="submit"
            :disabled="isLoading"
            class="btn btn-primary w-full"
          >
            <span v-if="isLoading" class="loading">Signing in...</span>
            <span v-else>Sign in</span>
          </button>
        </div>
      </form>
    </div>

    <!-- Registration Form -->
    <div v-else>
      <form @submit.prevent="handleRegister" class="space-y-6">
        <div class="grid grid-cols-1 gap-6 sm:grid-cols-2">
          <div>
            <label for="first_name" class="label">First name</label>
            <input
              id="first_name"
              v-model="registerForm.first_name"
              type="text"
              required
              class="input"
              placeholder="First name"
            />
          </div>

          <div>
            <label for="last_name" class="label">Last name</label>
            <input
              id="last_name"
              v-model="registerForm.last_name"
              type="text"
              required
              class="input"
              placeholder="Last name"
            />
          </div>
        </div>

        <div>
          <label for="email" class="label">Email address</label>
          <input
            id="email"
            v-model="registerForm.email"
            type="email"
            required
            class="input"
            placeholder="Enter your email"
          />
        </div>

        <div>
          <label for="phone" class="label">Phone number</label>
          <input
            id="phone"
            v-model="registerForm.phone"
            type="tel"
            required
            class="input"
            placeholder="+234 800 000 0000"
          />
        </div>

        <div>
          <label for="password" class="label">Password</label>
          <input
            id="password"
            v-model="registerForm.password"
            type="password"
            required
            class="input"
            placeholder="Create a password"
          />
        </div>

        <div>
          <label for="password_confirmation" class="label">Confirm password</label>
          <input
            id="password_confirmation"
            v-model="registerForm.password_confirmation"
            type="password"
            required
            class="input"
            placeholder="Confirm your password"
          />
        </div>

        <div>
          <label for="business_name" class="label">Business name (optional)</label>
          <input
            id="business_name"
            v-model="registerForm.business_name"
            type="text"
            class="input"
            placeholder="Your business name"
          />
        </div>

        <div class="flex items-center">
          <input
            id="terms"
            v-model="registerForm.accept_terms"
            type="checkbox"
            required
            class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
          />
          <label for="terms" class="ml-2 block text-sm text-gray-900">
            I agree to the
            <a href="#" class="text-blue-600 hover:text-blue-500">Terms and Conditions</a>
          </label>
        </div>

        <div class="flex space-x-4">
          <button
            type="button"
            @click="showRegister = false"
            class="btn btn-secondary flex-1"
          >
            Back to Login
          </button>
          <button
            type="submit"
            :disabled="isLoading"
            class="btn btn-primary flex-1"
          >
            <span v-if="isLoading" class="loading">Creating account...</span>
            <span v-else>Create account</span>
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const showRegister = ref(false)
const isLoading = ref(false)

const loginForm = reactive({
  email: '',
  password: '',
  remember: false
})

const registerForm = reactive({
  first_name: '',
  last_name: '',
  email: '',
  phone: '',
  password: '',
  password_confirmation: '',
  business_name: '',
  accept_terms: false
})

const handleLogin = async () => {
  isLoading.value = true
  try {
    await authStore.login(loginForm)
    router.push('/')
  } catch (error) {
    console.error('Login failed:', error)
  } finally {
    isLoading.value = false
  }
}

const handleRegister = async () => {
  if (registerForm.password !== registerForm.password_confirmation) {
    alert('Passwords do not match')
    return
  }

  isLoading.value = true
  try {
    await authStore.register(registerForm)
    router.push('/')
  } catch (error) {
    console.error('Registration failed:', error)
  } finally {
    isLoading.value = false
  }
}
</script>
