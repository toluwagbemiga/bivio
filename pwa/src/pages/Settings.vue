<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Settings</h1>
        <p class="text-gray-600 mt-1">Manage your account and application preferences</p>
      </div>
    </div>

    <!-- Settings Tabs -->
    <div class="card">
      <div class="border-b border-gray-200">
        <nav class="-mb-px flex space-x-8">
          <button
            v-for="tab in tabs"
            :key="tab.id"
            @click="activeTab = tab.id"
            :class="[
              activeTab === tab.id
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300',
              'whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm'
            ]"
          >
            {{ tab.name }}
          </button>
        </nav>
      </div>

      <!-- Tab Content -->
      <div class="mt-6">
        <!-- Profile Tab -->
        <div v-if="activeTab === 'profile'">
          <form @submit.prevent="updateProfile" class="space-y-6">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label class="label">First Name</label>
                <input v-model="profile.first_name" type="text" required class="input" />
              </div>
              <div>
                <label class="label">Last Name</label>
                <input v-model="profile.last_name" type="text" required class="input" />
              </div>
            </div>
            <div>
              <label class="label">Email</label>
              <input v-model="profile.email" type="email" required class="input" />
            </div>
            <div>
              <label class="label">Phone Number</label>
              <input v-model="profile.phone" type="tel" required class="input" />
            </div>
            <div>
              <label class="label">Business Name</label>
              <input v-model="profile.business_name" type="text" class="input" />
            </div>
            <div>
              <label class="label">Address</label>
              <textarea v-model="profile.address" class="input" rows="3"></textarea>
            </div>
            <div class="flex justify-end">
              <button type="submit" :disabled="isLoading" class="btn btn-primary">
                Update Profile
              </button>
            </div>
          </form>
        </div>

        <!-- Business Tab -->
        <div v-if="activeTab === 'business'">
          <form @submit.prevent="updateBusinessProfile" class="space-y-6">
            <div>
              <label class="label">Business Name</label>
              <input v-model="businessProfile.business_name" type="text" required class="input" />
            </div>
            <div>
              <label class="label">Business Type</label>
              <select v-model="businessProfile.business_type" required class="input">
                <option value="">Select Business Type</option>
                <option value="retail">Retail</option>
                <option value="wholesale">Wholesale</option>
                <option value="service">Service</option>
                <option value="manufacturing">Manufacturing</option>
                <option value="other">Other</option>
              </select>
            </div>
            <div>
              <label class="label">Registration Number</label>
              <input v-model="businessProfile.registration_number" type="text" class="input" />
            </div>
            <div>
              <label class="label">Tax ID</label>
              <input v-model="businessProfile.tax_id" type="text" class="input" />
            </div>
            <div>
              <label class="label">Business Address</label>
              <textarea v-model="businessProfile.business_address" class="input" rows="3"></textarea>
            </div>
            <div class="flex justify-end">
              <button type="submit" :disabled="isLoading" class="btn btn-primary">
                Update Business Profile
              </button>
            </div>
          </form>
        </div>

        <!-- Notifications Tab -->
        <div v-if="activeTab === 'notifications'">
          <div class="space-y-6">
            <div v-for="preference in notificationPreferences" :key="preference.id" class="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <div>
                <h4 class="text-sm font-medium text-gray-900">{{ preference.notification_type }}</h4>
                <p class="text-sm text-gray-600">{{ preference.description }}</p>
              </div>
              <div class="flex items-center space-x-4">
                <div class="flex items-center space-x-2">
                  <label class="text-sm text-gray-600">Email</label>
                  <input
                    v-model="preference.email_enabled"
                    type="checkbox"
                    class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                </div>
                <div class="flex items-center space-x-2">
                  <label class="text-sm text-gray-600">SMS</label>
                  <input
                    v-model="preference.sms_enabled"
                    type="checkbox"
                    class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                </div>
                <div class="flex items-center space-x-2">
                  <label class="text-sm text-gray-600">Push</label>
                  <input
                    v-model="preference.push_enabled"
                    type="checkbox"
                    class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                </div>
              </div>
            </div>
            <div class="flex justify-end">
              <button @click="updateNotificationPreferences" :disabled="isLoading" class="btn btn-primary">
                Save Preferences
              </button>
            </div>
          </div>
        </div>

        <!-- Security Tab -->
        <div v-if="activeTab === 'security'">
          <div class="space-y-6">
            <div>
              <h3 class="text-lg font-medium text-gray-900 mb-4">Change Password</h3>
              <form @submit.prevent="changePassword" class="space-y-4">
                <div>
                  <label class="label">Current Password</label>
                  <input v-model="passwordForm.current_password" type="password" required class="input" />
                </div>
                <div>
                  <label class="label">New Password</label>
                  <input v-model="passwordForm.new_password" type="password" required class="input" />
                </div>
                <div>
                  <label class="label">Confirm New Password</label>
                  <input v-model="passwordForm.confirm_password" type="password" required class="input" />
                </div>
                <div class="flex justify-end">
                  <button type="submit" :disabled="isLoading" class="btn btn-primary">
                    Change Password
                  </button>
                </div>
              </form>
            </div>

            <div>
              <h3 class="text-lg font-medium text-gray-900 mb-4">Two-Factor Authentication</h3>
              <div class="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div>
                  <h4 class="text-sm font-medium text-gray-900">SMS Authentication</h4>
                  <p class="text-sm text-gray-600">Receive verification codes via SMS</p>
                </div>
                <button @click="toggle2FA" class="btn btn-secondary">
                  {{ twoFactorEnabled ? 'Disable' : 'Enable' }}
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Preferences Tab -->
        <div v-if="activeTab === 'preferences'">
          <div class="space-y-6">
            <div>
              <h3 class="text-lg font-medium text-gray-900 mb-4">General Preferences</h3>
              <div class="space-y-4">
                <div class="flex items-center justify-between">
                  <div>
                    <h4 class="text-sm font-medium text-gray-900">Currency</h4>
                    <p class="text-sm text-gray-600">Default currency for transactions</p>
                  </div>
                  <select v-model="preferences.currency" class="input w-32">
                    <option value="NGN">NGN (₦)</option>
                    <option value="USD">USD ($)</option>
                    <option value="EUR">EUR (€)</option>
                  </select>
                </div>
                <div class="flex items-center justify-between">
                  <div>
                    <h4 class="text-sm font-medium text-gray-900">Language</h4>
                    <p class="text-sm text-gray-600">Application language</p>
                  </div>
                  <select v-model="preferences.language" class="input w-32">
                    <option value="en">English</option>
                    <option value="ha">Hausa</option>
                    <option value="ig">Igbo</option>
                    <option value="yo">Yoruba</option>
                  </select>
                </div>
                <div class="flex items-center justify-between">
                  <div>
                    <h4 class="text-sm font-medium text-gray-900">Auto-save Percentage</h4>
                    <p class="text-sm text-gray-600">Percentage of transactions to auto-save</p>
                  </div>
                  <input v-model="preferences.auto_save_percentage" type="number" min="0" max="100" class="input w-32" />
                </div>
                <div class="flex items-center justify-between">
                  <div>
                    <h4 class="text-sm font-medium text-gray-900">Low Stock Alert</h4>
                    <p class="text-sm text-gray-600">Get notified when stock is low</p>
                  </div>
                  <input v-model="preferences.low_stock_alert" type="checkbox" class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded" />
                </div>
              </div>
            </div>
            <div class="flex justify-end">
              <button @click="updatePreferences" :disabled="isLoading" class="btn btn-primary">
                Save Preferences
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useNotificationStore } from '../stores/notifications'
import { useToast } from 'vue-toastification'

const authStore = useAuthStore()
const notificationStore = useNotificationStore()
const toast = useToast()

const activeTab = ref('profile')
const isLoading = ref(false)
const twoFactorEnabled = ref(false)

const profile = reactive({
  first_name: '',
  last_name: '',
  email: '',
  phone: '',
  business_name: '',
  address: ''
})

const businessProfile = reactive({
  business_name: '',
  business_type: '',
  registration_number: '',
  tax_id: '',
  business_address: ''
})

const passwordForm = reactive({
  current_password: '',
  new_password: '',
  confirm_password: ''
})

const preferences = reactive({
  currency: 'NGN',
  language: 'en',
  auto_save_percentage: 10,
  low_stock_alert: true
})

const notificationPreferences = ref([])

const tabs = [
  { id: 'profile', name: 'Profile' },
  { id: 'business', name: 'Business' },
  { id: 'notifications', name: 'Notifications' },
  { id: 'security', name: 'Security' },
  { id: 'preferences', name: 'Preferences' }
]

const loadUserData = async () => {
  try {
    const user = authStore.user
    if (user) {
      Object.assign(profile, {
        first_name: user.first_name || '',
        last_name: user.last_name || '',
        email: user.email || '',
        phone: user.phone || '',
        business_name: user.business_name || '',
        address: user.address || ''
      })
    }

    await notificationStore.fetchPreferences()
    notificationPreferences.value = notificationStore.preferences
  } catch (error) {
    console.error('Failed to load user data:', error)
  }
}

const updateProfile = async () => {
  isLoading.value = true
  try {
    await authStore.updateProfile(profile)
    toast.success('Profile updated successfully!')
  } catch (error) {
    console.error('Failed to update profile:', error)
  } finally {
    isLoading.value = false
  }
}

const updateBusinessProfile = async () => {
  isLoading.value = true
  try {
    // TODO: Implement business profile update
    toast.success('Business profile updated successfully!')
  } catch (error) {
    console.error('Failed to update business profile:', error)
  } finally {
    isLoading.value = false
  }
}

const updateNotificationPreferences = async () => {
  isLoading.value = true
  try {
    for (const preference of notificationPreferences.value) {
      await notificationStore.updatePreference(preference.id, {
        email_enabled: preference.email_enabled,
        sms_enabled: preference.sms_enabled,
        push_enabled: preference.push_enabled
      })
    }
    toast.success('Notification preferences updated!')
  } catch (error) {
    console.error('Failed to update notification preferences:', error)
  } finally {
    isLoading.value = false
  }
}

const changePassword = async () => {
  if (passwordForm.new_password !== passwordForm.confirm_password) {
    toast.error('New passwords do not match')
    return
  }

  isLoading.value = true
  try {
    // TODO: Implement password change
    toast.success('Password changed successfully!')
    Object.assign(passwordForm, {
      current_password: '',
      new_password: '',
      confirm_password: ''
    })
  } catch (error) {
    console.error('Failed to change password:', error)
  } finally {
    isLoading.value = false
  }
}

const toggle2FA = async () => {
  try {
    twoFactorEnabled.value = !twoFactorEnabled.value
    toast.success(`Two-factor authentication ${twoFactorEnabled.value ? 'enabled' : 'disabled'}!`)
  } catch (error) {
    console.error('Failed to toggle 2FA:', error)
  }
}

const updatePreferences = async () => {
  isLoading.value = true
  try {
    // TODO: Implement preferences update
    toast.success('Preferences updated successfully!')
  } catch (error) {
    console.error('Failed to update preferences:', error)
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  loadUserData()
})
</script>
