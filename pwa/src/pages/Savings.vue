<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Savings & Goals</h1>
        <p class="text-gray-600 mt-1">Manage your savings accounts and financial goals</p>
      </div>
      <div class="flex space-x-3">
        <button @click="showCreateAccount = true" class="btn btn-primary">
          <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
          </svg>
          Create Account
        </button>
        <button @click="showCreateGoal = true" class="btn btn-success">
          <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          Set Goal
        </button>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
      <div class="card">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <div class="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center">
              <svg class="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
              </svg>
            </div>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">Total Savings</p>
            <p class="text-2xl font-semibold text-gray-900">₦{{ formatCurrency(totalSavings) }}</p>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <div class="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
              <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
              </svg>
            </div>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">Active Accounts</p>
            <p class="text-2xl font-semibold text-gray-900">{{ activeAccounts.length }}</p>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <div class="w-8 h-8 bg-purple-100 rounded-lg flex items-center justify-center">
              <svg class="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">Active Goals</p>
            <p class="text-2xl font-semibold text-gray-900">{{ activeGoals.length }}</p>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <div class="w-8 h-8 bg-yellow-100 rounded-lg flex items-center justify-center">
              <svg class="w-5 h-5 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
              </svg>
            </div>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">This Month</p>
            <p class="text-2xl font-semibold text-gray-900">₦{{ formatCurrency(monthlySavings) }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Tabs -->
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
            <span v-if="tab.count" class="ml-2 bg-gray-100 text-gray-900 py-0.5 px-2.5 rounded-full text-xs">
              {{ tab.count }}
            </span>
          </button>
        </nav>
      </div>

      <!-- Tab Content -->
      <div class="mt-6">
        <!-- Accounts Tab -->
        <div v-if="activeTab === 'accounts'">
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div v-for="account in savingsAccounts" :key="account.id" class="card">
              <div class="flex items-center justify-between mb-4">
                <h3 class="text-lg font-medium text-gray-900">{{ account.account_name }}</h3>
                <span class="badge" :class="getAccountStatusClass(account.status)">
                  {{ account.status }}
                </span>
              </div>
              <div class="space-y-2">
                <div class="flex justify-between">
                  <span class="text-sm text-gray-500">Balance:</span>
                  <span class="text-lg font-semibold text-gray-900">₦{{ formatCurrency(account.balance) }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-sm text-gray-500">Interest Rate:</span>
                  <span class="text-sm font-medium">{{ account.interest_rate }}%</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-sm text-gray-500">Account Type:</span>
                  <span class="text-sm font-medium">{{ account.account_type }}</span>
                </div>
              </div>
              <div class="mt-4 flex space-x-2">
                <button @click="depositToAccount(account)" class="btn btn-success flex-1">
                  Deposit
                </button>
                <button @click="withdrawFromAccount(account)" class="btn btn-secondary flex-1">
                  Withdraw
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Goals Tab -->
        <div v-if="activeTab === 'goals'">
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div v-for="goal in savingsGoals" :key="goal.id" class="card">
              <div class="flex items-center justify-between mb-4">
                <h3 class="text-lg font-medium text-gray-900">{{ goal.goal_name }}</h3>
                <span class="badge" :class="getGoalStatusClass(goal.status)">
                  {{ goal.status }}
                </span>
              </div>
              <div class="space-y-2">
                <div class="flex justify-between">
                  <span class="text-sm text-gray-500">Target:</span>
                  <span class="text-sm font-medium">₦{{ formatCurrency(goal.target_amount) }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-sm text-gray-500">Saved:</span>
                  <span class="text-sm font-medium">₦{{ formatCurrency(goal.current_amount) }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-sm text-gray-500">Progress:</span>
                  <span class="text-sm font-medium">{{ Math.round((goal.current_amount / goal.target_amount) * 100) }}%</span>
                </div>
              </div>
              <div class="mt-4">
                <div class="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    class="bg-blue-600 h-2 rounded-full" 
                    :style="{ width: `${Math.min((goal.current_amount / goal.target_amount) * 100, 100)}%` }"
                  ></div>
                </div>
              </div>
              <div class="mt-4">
                <button @click="contributeToGoal(goal)" class="btn btn-primary w-full">
                  Contribute
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Transactions Tab -->
        <div v-if="activeTab === 'transactions'">
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Transaction
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Account
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Type
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Amount
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Date
                  </th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr v-for="transaction in savingsTransactions" :key="transaction.id">
                  <td class="px-6 py-4 whitespace-nowrap">
                    <div class="text-sm font-medium text-gray-900">
                      {{ transaction.reference_number }}
                    </div>
                    <div class="text-sm text-gray-500">
                      {{ transaction.description || 'No description' }}
                    </div>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {{ transaction.savings_account?.account_name }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap">
                    <span class="badge" :class="getTransactionTypeClass(transaction.transaction_type)">
                      {{ transaction.transaction_type }}
                    </span>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    ₦{{ formatCurrency(transaction.amount) }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {{ formatDate(transaction.transaction_date) }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- Create Account Modal -->
    <div v-if="showCreateAccount" class="fixed inset-0 z-50 overflow-hidden">
      <div class="absolute inset-0 bg-black bg-opacity-25" @click="showCreateAccount = false"></div>
      <div class="absolute inset-0 flex items-center justify-center p-4">
        <div class="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
          <h3 class="text-lg font-medium text-gray-900 mb-4">Create Savings Account</h3>
          <form @submit.prevent="handleCreateAccount">
            <div class="space-y-4">
              <div>
                <label class="label">Account Name</label>
                <input v-model="newAccount.account_name" type="text" required class="input" />
              </div>
              <div>
                <label class="label">Account Type</label>
                <select v-model="newAccount.account_type" required class="input">
                  <option value="">Select Account Type</option>
                  <option value="regular">Regular Savings</option>
                  <option value="fixed_deposit">Fixed Deposit</option>
                  <option value="target_savings">Target Savings</option>
                </select>
              </div>
              <div>
                <label class="label">Initial Deposit</label>
                <input v-model="newAccount.initial_deposit" type="number" step="0.01" class="input" />
              </div>
              <div>
                <label class="label">Description (Optional)</label>
                <textarea v-model="newAccount.description" class="input" rows="3"></textarea>
              </div>
            </div>
            <div class="flex justify-end space-x-3 mt-6">
              <button type="button" @click="showCreateAccount = false" class="btn btn-secondary">
                Cancel
              </button>
              <button type="submit" :disabled="isLoading" class="btn btn-primary">
                Create Account
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Create Goal Modal -->
    <div v-if="showCreateGoal" class="fixed inset-0 z-50 overflow-hidden">
      <div class="absolute inset-0 bg-black bg-opacity-25" @click="showCreateGoal = false"></div>
      <div class="absolute inset-0 flex items-center justify-center p-4">
        <div class="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
          <h3 class="text-lg font-medium text-gray-900 mb-4">Set Savings Goal</h3>
          <form @submit.prevent="handleCreateGoal">
            <div class="space-y-4">
              <div>
                <label class="label">Goal Name</label>
                <input v-model="newGoal.goal_name" type="text" required class="input" />
              </div>
              <div>
                <label class="label">Target Amount</label>
                <input v-model="newGoal.target_amount" type="number" step="0.01" required class="input" />
              </div>
              <div>
                <label class="label">Target Date</label>
                <input v-model="newGoal.target_date" type="date" required class="input" />
              </div>
              <div>
                <label class="label">Savings Account</label>
                <select v-model="newGoal.savings_account" required class="input">
                  <option value="">Select Account</option>
                  <option v-for="account in savingsAccounts" :key="account.id" :value="account.id">
                    {{ account.account_name }}
                  </option>
                </select>
              </div>
              <div>
                <label class="label">Description (Optional)</label>
                <textarea v-model="newGoal.description" class="input" rows="3"></textarea>
              </div>
            </div>
            <div class="flex justify-end space-x-3 mt-6">
              <button type="button" @click="showCreateGoal = false" class="btn btn-secondary">
                Cancel
              </button>
              <button type="submit" :disabled="isLoading" class="btn btn-primary">
                Create Goal
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { savingsApi } from '../services/api/savings'
import { useToast } from 'vue-toastification'

const toast = useToast()

const showCreateAccount = ref(false)
const showCreateGoal = ref(false)
const isLoading = ref(false)
const activeTab = ref('accounts')

const savingsAccounts = ref([])
const savingsGoals = ref([])
const savingsTransactions = ref([])

const newAccount = ref({
  account_name: '',
  account_type: '',
  initial_deposit: '',
  description: ''
})

const newGoal = ref({
  goal_name: '',
  target_amount: '',
  target_date: '',
  savings_account: '',
  description: ''
})

const tabs = computed(() => [
  { id: 'accounts', name: 'Savings Accounts', count: savingsAccounts.value.length },
  { id: 'goals', name: 'Savings Goals', count: savingsGoals.value.length },
  { id: 'transactions', name: 'Transactions', count: savingsTransactions.value.length }
])

const activeAccounts = computed(() => 
  savingsAccounts.value.filter(account => account.status === 'active')
)

const activeGoals = computed(() => 
  savingsGoals.value.filter(goal => goal.status === 'active')
)

const totalSavings = computed(() => 
  savingsAccounts.value.reduce((total, account) => total + parseFloat(account.balance), 0)
)

const monthlySavings = computed(() => {
  const currentMonth = new Date().getMonth()
  const currentYear = new Date().getFullYear()
  
  return savingsTransactions.value
    .filter(transaction => {
      const transactionDate = new Date(transaction.transaction_date)
      return transactionDate.getMonth() === currentMonth && 
             transactionDate.getFullYear() === currentYear &&
             transaction.transaction_type === 'deposit'
    })
    .reduce((total, transaction) => total + parseFloat(transaction.amount), 0)
})

const formatCurrency = (amount) => {
  return new Intl.NumberFormat('en-NG', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(amount)
}

const formatDate = (date) => {
  return new Date(date).toLocaleDateString('en-NG', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

const getAccountStatusClass = (status) => {
  const classes = {
    'active': 'badge-success',
    'inactive': 'badge-warning',
    'suspended': 'badge-danger'
  }
  return classes[status] || 'badge-info'
}

const getGoalStatusClass = (status) => {
  const classes = {
    'active': 'badge-success',
    'completed': 'badge-info',
    'paused': 'badge-warning',
    'cancelled': 'badge-danger'
  }
  return classes[status] || 'badge-info'
}

const getTransactionTypeClass = (type) => {
  const classes = {
    'deposit': 'badge-success',
    'withdrawal': 'badge-warning',
    'auto_save': 'badge-info',
    'interest': 'badge-info'
  }
  return classes[type] || 'badge-info'
}

const loadData = async () => {
  try {
    const [accountsData, goalsData, transactionsData] = await Promise.all([
      savingsApi.getSavingsAccounts(),
      savingsApi.getSavingsGoals(),
      savingsApi.getSavingsTransactions()
    ])
    
    savingsAccounts.value = accountsData.results || accountsData
    savingsGoals.value = goalsData.results || goalsData
    savingsTransactions.value = transactionsData.results || transactionsData
  } catch (error) {
    console.error('Failed to load savings data:', error)
  }
}

const handleCreateAccount = async () => {
  isLoading.value = true
  try {
    await savingsApi.createSavingsAccount(newAccount.value)
    showCreateAccount.value = false
    resetNewAccount()
    await loadData()
    toast.success('Savings account created successfully!')
  } catch (error) {
    console.error('Failed to create account:', error)
  } finally {
    isLoading.value = false
  }
}

const handleCreateGoal = async () => {
  isLoading.value = true
  try {
    await savingsApi.createSavingsGoal(newGoal.value)
    showCreateGoal.value = false
    resetNewGoal()
    await loadData()
    toast.success('Savings goal created successfully!')
  } catch (error) {
    console.error('Failed to create goal:', error)
  } finally {
    isLoading.value = false
  }
}

const resetNewAccount = () => {
  newAccount.value = {
    account_name: '',
    account_type: '',
    initial_deposit: '',
    description: ''
  }
}

const resetNewGoal = () => {
  newGoal.value = {
    goal_name: '',
    target_amount: '',
    target_date: '',
    savings_account: '',
    description: ''
  }
}

const depositToAccount = (account) => {
  // TODO: Implement deposit modal
  toast.info('Deposit functionality coming soon!')
}

const withdrawFromAccount = (account) => {
  // TODO: Implement withdrawal modal
  toast.info('Withdrawal functionality coming soon!')
}

const contributeToGoal = (goal) => {
  // TODO: Implement goal contribution modal
  toast.info('Goal contribution coming soon!')
}

onMounted(() => {
  loadData()
})
</script>
