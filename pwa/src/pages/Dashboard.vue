<template>
  <div class="space-y-6">
    <!-- Welcome Header -->
    <div class="bg-white rounded-lg shadow-sm p-6">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-2xl font-bold text-gray-900">
            Welcome back, {{ user?.first_name || 'User' }}!
          </h1>
          <p class="text-gray-600 mt-1">
            Here's what's happening with your business today
          </p>
        </div>
        <div class="text-right">
          <p class="text-sm text-gray-500">Today</p>
          <p class="text-lg font-semibold text-gray-900">
            {{ formatDate(new Date()) }}
          </p>
        </div>
      </div>
    </div>

    <!-- Quick Stats -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
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
            <p class="text-2xl font-semibold text-gray-900">
              ₦{{ formatCurrency(dashboardStats.today_sales || 0) }}
            </p>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <div class="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
              <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
              </svg>
            </div>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">Total Products</p>
            <p class="text-2xl font-semibold text-gray-900">
              {{ dashboardStats.total_products || 0 }}
            </p>
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
            <p class="text-sm font-medium text-gray-500">Low Stock</p>
            <p class="text-2xl font-semibold text-gray-900">
              {{ dashboardStats.low_stock_count || 0 }}
            </p>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <div class="w-8 h-8 bg-purple-100 rounded-lg flex items-center justify-center">
              <svg class="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">Active Loans</p>
            <p class="text-2xl font-semibold text-gray-900">
              {{ dashboardStats.active_loans || 0 }}
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- Charts Row -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Sales Chart -->
      <div class="card">
        <h3 class="text-lg font-medium text-gray-900 mb-4">Sales Trend (Last 7 Days)</h3>
        <div class="h-64">
          <canvas ref="salesChart"></canvas>
        </div>
      </div>

      <!-- Top Products -->
      <div class="card">
        <h3 class="text-lg font-medium text-gray-900 mb-4">Top Selling Products</h3>
        <div class="space-y-3">
          <div v-for="product in topProducts" :key="product.id" class="flex items-center justify-between">
            <div class="flex items-center">
              <div class="w-10 h-10 bg-gray-100 rounded-lg flex items-center justify-center">
                <svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
                </svg>
              </div>
              <div class="ml-3">
                <p class="text-sm font-medium text-gray-900">{{ product.name }}</p>
                <p class="text-sm text-gray-500">{{ product.category?.name }}</p>
              </div>
            </div>
            <div class="text-right">
              <p class="text-sm font-medium text-gray-900">{{ product.total_sold || 0 }}</p>
              <p class="text-sm text-gray-500">sold</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Recent Transactions -->
    <div class="card">
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-lg font-medium text-gray-900">Recent Transactions</h3>
        <router-link to="/transactions" class="text-sm text-blue-600 hover:text-blue-500">
          View all
        </router-link>
      </div>
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
                Status
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Date
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="transaction in recentTransactions" :key="transaction.id">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900">
                  {{ transaction.reference_number }}
                </div>
                <div class="text-sm text-gray-500">
                  {{ transaction.description || 'No description' }}
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
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="badge" :class="getStatusClass(transaction.status)">
                  {{ transaction.status }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ formatDate(transaction.transaction_date) }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="card">
      <h3 class="text-lg font-medium text-gray-900 mb-4">Quick Actions</h3>
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <router-link to="/transactions" class="btn btn-primary text-center">
          <svg class="w-5 h-5 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
          </svg>
          New Sale
        </router-link>
        <router-link to="/inventory" class="btn btn-secondary text-center">
          <svg class="w-5 h-5 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
          </svg>
          Add Product
        </router-link>
        <router-link to="/loans" class="btn btn-secondary text-center">
          <svg class="w-5 h-5 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          Apply Loan
        </router-link>
        <router-link to="/savings" class="btn btn-secondary text-center">
          <svg class="w-5 h-5 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
          </svg>
          Add Savings
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useInventoryStore } from '../stores/inventory'
import { useTransactionStore } from '../stores/transactions'
import { Chart, registerables } from 'chart.js'

Chart.register(...registerables)

const authStore = useAuthStore()
const inventoryStore = useInventoryStore()
const transactionStore = useTransactionStore()

const salesChart = ref(null)
const dashboardStats = ref({})
const topProducts = ref([])
const recentTransactions = ref([])

const user = computed(() => authStore.user)

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

const loadDashboardData = async () => {
  try {
    // Load dashboard stats
    const stats = await inventoryStore.getDashboardStats()
    dashboardStats.value = stats

    // Load top products
    const products = await inventoryStore.fetchProducts({ limit: 5, ordering: '-total_sold' })
    topProducts.value = products.results || products

    // Load recent transactions
    const transactions = await transactionStore.fetchTransactions({ limit: 5 })
    recentTransactions.value = transactions.results || transactions

    // Create sales chart
    createSalesChart()
  } catch (error) {
    console.error('Failed to load dashboard data:', error)
  }
}

const createSalesChart = () => {
  if (!salesChart.value) return

  const ctx = salesChart.value.getContext('2d')
  
  // Mock data for demonstration
  const salesData = {
    labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    datasets: [{
      label: 'Sales (₦)',
      data: [12000, 19000, 15000, 25000, 22000, 30000, 28000],
      borderColor: 'rgb(59, 130, 246)',
      backgroundColor: 'rgba(59, 130, 246, 0.1)',
      tension: 0.4
    }]
  }

  new Chart(ctx, {
    type: 'line',
    data: salesData,
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            callback: function(value) {
              return '₦' + value.toLocaleString()
            }
          }
        }
      }
    }
  })
}

onMounted(() => {
  loadDashboardData()
})
</script>
