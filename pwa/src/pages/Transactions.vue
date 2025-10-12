<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Transactions</h1>
        <p class="text-gray-600 mt-1">Manage sales, purchases, and payments</p>
      </div>
      <div class="flex space-x-3">
        <button @click="showNewTransaction = true" class="btn btn-primary">
          <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
          </svg>
          New Transaction
        </button>
        <button @click="showPOSSale = true" class="btn btn-success">
          <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
          </svg>
          POS Sale
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
            <p class="text-sm font-medium text-gray-500">Today's Sales</p>
            <p class="text-2xl font-semibold text-gray-900">₦{{ formatCurrency(totalSalesToday) }}</p>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <div class="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
              <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
            </div>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">Total Transactions</p>
            <p class="text-2xl font-semibold text-gray-900">{{ transactions.length }}</p>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <div class="w-8 h-8 bg-purple-100 rounded-lg flex items-center justify-center">
              <svg class="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
              </svg>
            </div>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">Pending</p>
            <p class="text-2xl font-semibold text-gray-900">{{ pendingTransactions.length }}</p>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <div class="w-8 h-8 bg-yellow-100 rounded-lg flex items-center justify-center">
              <svg class="w-5 h-5 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">Refunds</p>
            <p class="text-2xl font-semibold text-gray-900">{{ refundTransactions.length }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Filters -->
    <div class="card">
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-4 sm:space-y-0">
        <div class="flex flex-col sm:flex-row sm:items-center space-y-4 sm:space-y-0 sm:space-x-4">
          <div class="relative">
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Search transactions..."
              class="input pl-10"
            />
            <svg class="absolute left-3 top-3 h-4 w-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
          <select v-model="typeFilter" class="input">
            <option value="">All Types</option>
            <option value="sale">Sales</option>
            <option value="purchase">Purchases</option>
            <option value="refund">Refunds</option>
            <option value="transfer">Transfers</option>
          </select>
          <select v-model="statusFilter" class="input">
            <option value="">All Status</option>
            <option value="completed">Completed</option>
            <option value="pending">Pending</option>
            <option value="failed">Failed</option>
            <option value="cancelled">Cancelled</option>
          </select>
          <input
            v-model="dateFilter"
            type="date"
            class="input"
          />
        </div>
        <div class="flex items-center space-x-2">
          <button @click="refreshTransactions" class="btn btn-secondary">
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Refresh
          </button>
        </div>
      </div>
    </div>

    <!-- Transactions Table -->
    <div class="card">
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Transaction
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Type
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Amount
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Payment Method
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Date
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="transaction in filteredTransactions" :key="transaction.id">
              <td class="px-6 py-4 whitespace-nowrap">
                <div>
                  <div class="text-sm font-medium text-gray-900">
                    {{ transaction.reference_number }}
                  </div>
                  <div class="text-sm text-gray-500">
                    {{ transaction.description || 'No description' }}
                  </div>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="badge" :class="getTransactionTypeClass(transaction.transaction_type)">
                  {{ transaction.transaction_type }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                ₦{{ formatCurrency(transaction.total_amount) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {{ transaction.payment_method || 'N/A' }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="badge" :class="getStatusClass(transaction.status)">
                  {{ transaction.status }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ formatDate(transaction.transaction_date) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                <div class="flex space-x-2">
                  <button @click="viewTransaction(transaction)" class="text-blue-600 hover:text-blue-900">
                    View
                  </button>
                  <button v-if="transaction.transaction_type === 'sale'" @click="refundTransaction(transaction)" class="text-yellow-600 hover:text-yellow-900">
                    Refund
                  </button>
                  <button @click="categorizeTransaction(transaction)" class="text-green-600 hover:text-green-900">
                    Categorize
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- POS Sale Modal -->
    <div v-if="showPOSSale" class="fixed inset-0 z-50 overflow-hidden">
      <div class="absolute inset-0 bg-black bg-opacity-25" @click="showPOSSale = false"></div>
      <div class="absolute inset-0 flex items-center justify-center p-4">
        <div class="bg-white rounded-lg shadow-xl max-w-2xl w-full p-6">
          <h3 class="text-lg font-medium text-gray-900 mb-4">POS Sale</h3>
          <form @submit.prevent="handlePOSSale">
            <div class="space-y-4">
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="label">Customer Name (Optional)</label>
                  <input v-model="posSale.customer_name" type="text" class="input" />
                </div>
                <div>
                  <label class="label">Payment Method</label>
                  <select v-model="posSale.payment_method" required class="input">
                    <option value="">Select Payment Method</option>
                    <option value="cash">Cash</option>
                    <option value="card">Card</option>
                    <option value="transfer">Bank Transfer</option>
                    <option value="mobile_money">Mobile Money</option>
                  </select>
                </div>
              </div>
              
              <!-- Items -->
              <div>
                <label class="label">Items</label>
                <div class="space-y-2">
                  <div v-for="(item, index) in posSale.items" :key="index" class="flex space-x-2">
                    <select v-model="item.product_id" required class="input flex-1">
                      <option value="">Select Product</option>
                      <option v-for="product in products" :key="product.id" :value="product.id">
                        {{ product.name }} - ₦{{ formatCurrency(product.selling_price) }}
                      </option>
                    </select>
                    <input v-model="item.quantity" type="number" min="1" required class="input w-20" placeholder="Qty" />
                    <button type="button" @click="removeItem(index)" class="btn btn-danger">
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  </div>
                  <button type="button" @click="addItem" class="btn btn-secondary">
                    <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                    </svg>
                    Add Item
                  </button>
                </div>
              </div>

              <div>
                <label class="label">Total Amount</label>
                <input v-model="posSale.total_amount" type="number" step="0.01" readonly class="input bg-gray-100" />
              </div>

              <div>
                <label class="label">Notes (Optional)</label>
                <textarea v-model="posSale.notes" class="input" rows="3"></textarea>
              </div>
            </div>
            <div class="flex justify-end space-x-3 mt-6">
              <button type="button" @click="showPOSSale = false" class="btn btn-secondary">
                Cancel
              </button>
              <button type="submit" :disabled="isLoading" class="btn btn-primary">
                Process Sale
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useTransactionStore } from '../stores/transactions'
import { useInventoryStore } from '../stores/inventory'
import { useToast } from 'vue-toastification'

const transactionStore = useTransactionStore()
const inventoryStore = useInventoryStore()
const toast = useToast()

const showNewTransaction = ref(false)
const showPOSSale = ref(false)
const isLoading = ref(false)
const searchQuery = ref('')
const typeFilter = ref('')
const statusFilter = ref('')
const dateFilter = ref('')

const posSale = ref({
  customer_name: '',
  payment_method: '',
  items: [{ product_id: '', quantity: 1 }],
  total_amount: 0,
  notes: ''
})

const transactions = computed(() => transactionStore.transactions)
const products = computed(() => inventoryStore.products)
const todayTransactions = computed(() => transactionStore.todayTransactions)
const salesTransactions = computed(() => transactionStore.salesTransactions)
const totalSalesToday = computed(() => transactionStore.totalSalesToday)

const pendingTransactions = computed(() => 
  transactions.value.filter(t => t.status === 'pending')
)

const refundTransactions = computed(() => 
  transactions.value.filter(t => t.transaction_type === 'refund')
)

const filteredTransactions = computed(() => {
  let filtered = transactions.value

  if (searchQuery.value) {
    filtered = filtered.filter(transaction =>
      transaction.reference_number.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      (transaction.description && transaction.description.toLowerCase().includes(searchQuery.value.toLowerCase()))
    )
  }

  if (typeFilter.value) {
    filtered = filtered.filter(transaction => transaction.transaction_type === typeFilter.value)
  }

  if (statusFilter.value) {
    filtered = filtered.filter(transaction => transaction.status === statusFilter.value)
  }

  if (dateFilter.value) {
    filtered = filtered.filter(transaction => 
      new Date(transaction.transaction_date).toDateString() === new Date(dateFilter.value).toDateString()
    )
  }

  return filtered
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
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const getTransactionTypeClass = (type) => {
  const classes = {
    'sale': 'badge-success',
    'purchase': 'badge-info',
    'refund': 'badge-warning',
    'transfer': 'badge-info'
  }
  return classes[type] || 'badge-info'
}

const getStatusClass = (status) => {
  const classes = {
    'completed': 'badge-success',
    'pending': 'badge-warning',
    'failed': 'badge-danger',
    'cancelled': 'badge-danger'
  }
  return classes[status] || 'badge-info'
}

const refreshTransactions = async () => {
  await transactionStore.fetchTransactions()
  await transactionStore.fetchCategories()
}

const addItem = () => {
  posSale.value.items.push({ product_id: '', quantity: 1 })
}

const removeItem = (index) => {
  if (posSale.value.items.length > 1) {
    posSale.value.items.splice(index, 1)
  }
}

const calculateTotal = () => {
  let total = 0
  posSale.value.items.forEach(item => {
    if (item.product_id) {
      const product = products.value.find(p => p.id === item.product_id)
      if (product) {
        total += product.selling_price * item.quantity
      }
    }
  })
  posSale.value.total_amount = total
}

const handlePOSSale = async () => {
  isLoading.value = true
  try {
    const transactionData = {
      transaction_type: 'sale',
      customer_name: posSale.value.customer_name,
      payment_method: posSale.value.payment_method,
      total_amount: posSale.value.total_amount,
      notes: posSale.value.notes,
      items: posSale.value.items.filter(item => item.product_id)
    }
    
    await transactionStore.createTransaction(transactionData)
    showPOSSale.value = false
    resetPOSSale()
    toast.success('Sale processed successfully!')
  } catch (error) {
    console.error('Failed to process sale:', error)
  } finally {
    isLoading.value = false
  }
}

const resetPOSSale = () => {
  posSale.value = {
    customer_name: '',
    payment_method: '',
    items: [{ product_id: '', quantity: 1 }],
    total_amount: 0,
    notes: ''
  }
}

const viewTransaction = (transaction) => {
  // TODO: Implement transaction view modal
  toast.info('Transaction view coming soon!')
}

const refundTransaction = (transaction) => {
  // TODO: Implement refund functionality
  toast.info('Refund functionality coming soon!')
}

const categorizeTransaction = (transaction) => {
  // TODO: Implement categorization functionality
  toast.info('Categorization coming soon!')
}

// Watch for changes in POS sale items to recalculate total
watch(() => posSale.value.items, () => {
  calculateTotal()
}, { deep: true })

onMounted(async () => {
  await refreshTransactions()
  await inventoryStore.fetchProducts()
})
</script>
