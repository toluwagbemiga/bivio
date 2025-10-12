<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Loan Management</h1>
        <p class="text-gray-600 mt-1">Manage loan applications and repayments</p>
      </div>
      <div class="flex space-x-3">
        <button @click="showApplyLoan = true" class="btn btn-primary">
          <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          Apply for Loan
        </button>
        <button @click="showMakePayment = true" class="btn btn-success">
          <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
          </svg>
          Make Payment
        </button>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
      <div class="card">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <div class="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
              <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">Active Loans</p>
            <p class="text-2xl font-semibold text-gray-900">{{ activeLoans.length }}</p>
          </div>
        </div>
      </div>

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
            <p class="text-sm font-medium text-gray-500">Total Borrowed</p>
            <p class="text-2xl font-semibold text-gray-900">₦{{ formatCurrency(totalBorrowed) }}</p>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <div class="w-8 h-8 bg-yellow-100 rounded-lg flex items-center justify-center">
              <svg class="w-5 h-5 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
            </div>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">Outstanding</p>
            <p class="text-2xl font-semibold text-gray-900">₦{{ formatCurrency(totalOutstanding) }}</p>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <div class="w-8 h-8 bg-red-100 rounded-lg flex items-center justify-center">
              <svg class="w-5 h-5 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">Overdue</p>
            <p class="text-2xl font-semibold text-gray-900">{{ overdueLoans.length }}</p>
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
        <!-- My Loans Tab -->
        <div v-if="activeTab === 'my-loans'">
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Loan Details
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Amount
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Outstanding
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Next Payment
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr v-for="loan in myLoans" :key="loan.id">
                  <td class="px-6 py-4 whitespace-nowrap">
                    <div>
                      <div class="text-sm font-medium text-gray-900">
                        {{ loan.loan_product?.name }}
                      </div>
                      <div class="text-sm text-gray-500">
                        {{ loan.reference_number }}
                      </div>
                    </div>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    ₦{{ formatCurrency(loan.loan_amount) }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    ₦{{ formatCurrency(loan.outstanding_balance) }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap">
                    <span class="badge" :class="getLoanStatusClass(loan.status)">
                      {{ loan.status }}
                    </span>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {{ loan.next_payment_date ? formatDate(loan.next_payment_date) : 'N/A' }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <div class="flex space-x-2">
                      <button @click="viewLoan(loan)" class="text-blue-600 hover:text-blue-900">
                        View
                      </button>
                      <button v-if="loan.status === 'disbursed'" @click="makePayment(loan)" class="text-green-600 hover:text-green-900">
                        Pay
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Loan Products Tab -->
        <div v-if="activeTab === 'products'">
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div v-for="product in loanProducts" :key="product.id" class="card">
              <div class="flex items-center justify-between mb-4">
                <h3 class="text-lg font-medium text-gray-900">{{ product.name }}</h3>
                <span class="badge badge-success">{{ product.is_active ? 'Active' : 'Inactive' }}</span>
              </div>
              <div class="space-y-2">
                <div class="flex justify-between">
                  <span class="text-sm text-gray-500">Interest Rate:</span>
                  <span class="text-sm font-medium">{{ product.interest_rate }}%</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-sm text-gray-500">Min Amount:</span>
                  <span class="text-sm font-medium">₦{{ formatCurrency(product.min_amount) }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-sm text-gray-500">Max Amount:</span>
                  <span class="text-sm font-medium">₦{{ formatCurrency(product.max_amount) }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-sm text-gray-500">Duration:</span>
                  <span class="text-sm font-medium">{{ product.max_duration_months }} months</span>
                </div>
              </div>
              <div class="mt-4">
                <p class="text-sm text-gray-600">{{ product.description }}</p>
              </div>
              <div class="mt-4">
                <button @click="applyForLoan(product)" class="btn btn-primary w-full">
                  Apply Now
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Repayments Tab -->
        <div v-if="activeTab === 'repayments'">
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Loan
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Amount
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Due Date
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr v-for="repayment in repayments" :key="repayment.id">
                  <td class="px-6 py-4 whitespace-nowrap">
                    <div class="text-sm font-medium text-gray-900">
                      {{ repayment.loan?.reference_number }}
                    </div>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    ₦{{ formatCurrency(repayment.scheduled_amount) }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {{ formatDate(repayment.due_date) }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap">
                    <span class="badge" :class="getRepaymentStatusClass(repayment.status)">
                      {{ repayment.status }}
                    </span>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <button v-if="repayment.status === 'pending'" @click="payRepayment(repayment)" class="text-green-600 hover:text-green-900">
                      Pay Now
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- Apply for Loan Modal -->
    <div v-if="showApplyLoan" class="fixed inset-0 z-50 overflow-hidden">
      <div class="absolute inset-0 bg-black bg-opacity-25" @click="showApplyLoan = false"></div>
      <div class="absolute inset-0 flex items-center justify-center p-4">
        <div class="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
          <h3 class="text-lg font-medium text-gray-900 mb-4">Apply for Loan</h3>
          <form @submit.prevent="handleLoanApplication">
            <div class="space-y-4">
              <div>
                <label class="label">Loan Product</label>
                <select v-model="loanApplication.loan_product" required class="input">
                  <option value="">Select Loan Product</option>
                  <option v-for="product in loanProducts" :key="product.id" :value="product.id">
                    {{ product.name }} - {{ product.interest_rate }}% interest
                  </option>
                </select>
              </div>
              <div>
                <label class="label">Loan Amount</label>
                <input v-model="loanApplication.loan_amount" type="number" step="0.01" required class="input" />
              </div>
              <div>
                <label class="label">Duration (Months)</label>
                <input v-model="loanApplication.duration_months" type="number" required class="input" />
              </div>
              <div>
                <label class="label">Purpose</label>
                <textarea v-model="loanApplication.purpose" required class="input" rows="3"></textarea>
              </div>
              <div>
                <label class="label">Collateral Description (Optional)</label>
                <textarea v-model="loanApplication.collateral_description" class="input" rows="2"></textarea>
              </div>
            </div>
            <div class="flex justify-end space-x-3 mt-6">
              <button type="button" @click="showApplyLoan = false" class="btn btn-secondary">
                Cancel
              </button>
              <button type="submit" :disabled="isLoading" class="btn btn-primary">
                Submit Application
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
import { loanApi } from '../services/api/loans'
import { useToast } from 'vue-toastification'

const toast = useToast()

const showApplyLoan = ref(false)
const showMakePayment = ref(false)
const isLoading = ref(false)
const activeTab = ref('my-loans')

const loans = ref([])
const loanProducts = ref([])
const repayments = ref([])

const loanApplication = ref({
  loan_product: '',
  loan_amount: '',
  duration_months: '',
  purpose: '',
  collateral_description: ''
})

const tabs = computed(() => [
  { id: 'my-loans', name: 'My Loans', count: loans.value.length },
  { id: 'products', name: 'Loan Products', count: loanProducts.value.length },
  { id: 'repayments', name: 'Repayments', count: repayments.value.length }
])

const myLoans = computed(() => loans.value)
const activeLoans = computed(() => loans.value.filter(loan => loan.status === 'disbursed'))
const overdueLoans = computed(() => loans.value.filter(loan => loan.status === 'overdue'))

const totalBorrowed = computed(() => 
  loans.value.reduce((total, loan) => total + parseFloat(loan.loan_amount), 0)
)

const totalOutstanding = computed(() => 
  loans.value.reduce((total, loan) => total + parseFloat(loan.outstanding_balance), 0)
)

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

const getLoanStatusClass = (status) => {
  const classes = {
    'applied': 'badge-info',
    'under_review': 'badge-warning',
    'approved': 'badge-success',
    'disbursed': 'badge-success',
    'completed': 'badge-info',
    'overdue': 'badge-danger',
    'defaulted': 'badge-danger'
  }
  return classes[status] || 'badge-info'
}

const getRepaymentStatusClass = (status) => {
  const classes = {
    'pending': 'badge-warning',
    'completed': 'badge-success',
    'overdue': 'badge-danger',
    'partial': 'badge-info'
  }
  return classes[status] || 'badge-info'
}

const loadData = async () => {
  try {
    const [loansData, productsData, repaymentsData] = await Promise.all([
      loanApi.getMyLoans(),
      loanApi.getAvailableLoanProducts(),
      loanApi.getPendingRepayments()
    ])
    
    loans.value = loansData.results || loansData
    loanProducts.value = productsData.results || productsData
    repayments.value = repaymentsData.results || repaymentsData
  } catch (error) {
    console.error('Failed to load loan data:', error)
  }
}

const handleLoanApplication = async () => {
  isLoading.value = true
  try {
    await loanApi.createLoan(loanApplication.value)
    showApplyLoan.value = false
    resetLoanApplication()
    await loadData()
    toast.success('Loan application submitted successfully!')
  } catch (error) {
    console.error('Failed to submit loan application:', error)
  } finally {
    isLoading.value = false
  }
}

const resetLoanApplication = () => {
  loanApplication.value = {
    loan_product: '',
    loan_amount: '',
    duration_months: '',
    purpose: '',
    collateral_description: ''
  }
}

const applyForLoan = (product) => {
  loanApplication.value.loan_product = product.id
  showApplyLoan.value = true
}

const viewLoan = (loan) => {
  // TODO: Implement loan view modal
  toast.info('Loan details view coming soon!')
}

const makePayment = (loan) => {
  // TODO: Implement payment modal
  toast.info('Payment functionality coming soon!')
}

const payRepayment = (repayment) => {
  // TODO: Implement repayment payment
  toast.info('Repayment payment coming soon!')
}

onMounted(() => {
  loadData()
})
</script>
