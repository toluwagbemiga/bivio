<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Analytics & Insights</h1>
        <p class="text-gray-600 mt-1">Track your business performance and get AI insights</p>
      </div>
      <div class="flex space-x-3">
        <button @click="refreshAnalytics" class="btn btn-secondary">
          <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Refresh
        </button>
        <button @click="generateInsights" class="btn btn-primary">
          <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
          </svg>
          Generate Insights
        </button>
      </div>
    </div>

    <!-- Key Metrics -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <div class="card">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <div class="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center">
              <svg class="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
              </svg>
            </div>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">Revenue Growth</p>
            <p class="text-2xl font-semibold text-gray-900">{{ metrics.revenue_growth || 0 }}%</p>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <div class="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
              <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">Profit Margin</p>
            <p class="text-2xl font-semibold text-gray-900">{{ metrics.profit_margin || 0 }}%</p>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <div class="w-8 h-8 bg-purple-100 rounded-lg flex items-center justify-center">
              <svg class="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
              </svg>
            </div>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">Cash Flow</p>
            <p class="text-2xl font-semibold text-gray-900">₦{{ formatCurrency(metrics.cash_flow || 0) }}</p>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <div class="w-8 h-8 bg-yellow-100 rounded-lg flex items-center justify-center">
              <svg class="w-5 h-5 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">Business Score</p>
            <p class="text-2xl font-semibold text-gray-900">{{ metrics.business_score || 0 }}/100</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Charts Row -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Revenue Chart -->
      <div class="card">
        <h3 class="text-lg font-medium text-gray-900 mb-4">Revenue Trend (Last 30 Days)</h3>
        <div class="h-64">
          <canvas ref="revenueChart"></canvas>
        </div>
      </div>

      <!-- Cash Flow Chart -->
      <div class="card">
        <h3 class="text-lg font-medium text-gray-900 mb-4">Cash Flow Analysis</h3>
        <div class="h-64">
          <canvas ref="cashFlowChart"></canvas>
        </div>
      </div>
    </div>

    <!-- AI Insights -->
    <div class="card">
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-lg font-medium text-gray-900">AI Business Insights</h3>
        <span class="badge badge-info">{{ insights.length }} insights</span>
      </div>
      <div class="space-y-4">
        <div v-for="insight in insights" :key="insight.id" class="p-4 bg-gray-50 rounded-lg">
          <div class="flex items-start justify-between">
            <div class="flex-1">
              <div class="flex items-center mb-2">
                <span class="badge" :class="getInsightPriorityClass(insight.priority)">
                  {{ insight.priority }}
                </span>
                <span class="ml-2 text-sm text-gray-500">{{ formatDate(insight.created_at) }}</span>
              </div>
              <h4 class="text-sm font-medium text-gray-900 mb-1">{{ insight.title }}</h4>
              <p class="text-sm text-gray-600 mb-2">{{ insight.description }}</p>
              <div v-if="insight.recommendations" class="text-sm">
                <p class="font-medium text-gray-700 mb-1">Recommendations:</p>
                <ul class="list-disc list-inside text-gray-600">
                  <li v-for="recommendation in insight.recommendations" :key="recommendation">
                    {{ recommendation }}
                  </li>
                </ul>
              </div>
            </div>
            <div class="ml-4 flex space-x-2">
              <button @click="markInsightViewed(insight)" class="text-blue-600 hover:text-blue-900 text-sm">
                Mark Viewed
              </button>
              <button @click="rateInsight(insight)" class="text-green-600 hover:text-green-900 text-sm">
                Rate
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Performance Trends -->
    <div class="card">
      <h3 class="text-lg font-medium text-gray-900 mb-4">Performance Trends</h3>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div class="text-center">
          <div class="text-3xl font-bold text-green-600 mb-2">+{{ trends.sales_growth || 0 }}%</div>
          <div class="text-sm text-gray-600">Sales Growth</div>
          <div class="text-xs text-gray-500">vs last month</div>
        </div>
        <div class="text-center">
          <div class="text-3xl font-bold text-blue-600 mb-2">{{ trends.customer_retention || 0 }}%</div>
          <div class="text-sm text-gray-600">Customer Retention</div>
          <div class="text-xs text-gray-500">repeat customers</div>
        </div>
        <div class="text-center">
          <div class="text-3xl font-bold text-purple-600 mb-2">₦{{ formatCurrency(trends.avg_transaction || 0) }}</div>
          <div class="text-sm text-gray-600">Avg Transaction</div>
          <div class="text-xs text-gray-500">per customer</div>
        </div>
      </div>
    </div>

    <!-- Alert Rules -->
    <div class="card">
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-lg font-medium text-gray-900">Alert Rules</h3>
        <button @click="showCreateAlert = true" class="btn btn-primary">
          <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
          </svg>
          Create Alert
        </button>
      </div>
      <div class="space-y-3">
        <div v-for="alert in alertRules" :key="alert.id" class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
          <div>
            <div class="text-sm font-medium text-gray-900">{{ alert.name }}</div>
            <div class="text-sm text-gray-600">{{ alert.description }}</div>
          </div>
          <div class="flex items-center space-x-2">
            <span class="badge" :class="alert.is_active ? 'badge-success' : 'badge-warning'">
              {{ alert.is_active ? 'Active' : 'Inactive' }}
            </span>
            <button @click="toggleAlert(alert)" class="text-blue-600 hover:text-blue-900 text-sm">
              {{ alert.is_active ? 'Disable' : 'Enable' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { analyticsApi } from '../services/api/analytics'
import { useToast } from 'vue-toastification'
import { Chart, registerables } from 'chart.js'

Chart.register(...registerables)

const toast = useToast()

const showCreateAlert = ref(false)
const revenueChart = ref(null)
const cashFlowChart = ref(null)

const metrics = ref({})
const insights = ref([])
const trends = ref({})
const alertRules = ref([])

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

const getInsightPriorityClass = (priority) => {
  const classes = {
    'high': 'badge-danger',
    'medium': 'badge-warning',
    'low': 'badge-info'
  }
  return classes[priority] || 'badge-info'
}

const loadAnalyticsData = async () => {
  try {
    const [metricsData, insightsData, trendsData, alertsData] = await Promise.all([
      analyticsApi.getDashboard(),
      analyticsApi.getUnreadInsights(),
      analyticsApi.getPerformanceTrends(),
      analyticsApi.getActiveAlertRules()
    ])
    
    metrics.value = metricsData
    insights.value = insightsData.results || insightsData
    trends.value = trendsData
    alertRules.value = alertsData.results || alertsData
    
    // Create charts after data is loaded
    createCharts()
  } catch (error) {
    console.error('Failed to load analytics data:', error)
  }
}

const createCharts = () => {
  createRevenueChart()
  createCashFlowChart()
}

const createRevenueChart = () => {
  if (!revenueChart.value) return

  const ctx = revenueChart.value.getContext('2d')
  
  // Mock data for demonstration
  const revenueData = {
    labels: Array.from({ length: 30 }, (_, i) => {
      const date = new Date()
      date.setDate(date.getDate() - (29 - i))
      return date.toLocaleDateString('en-NG', { month: 'short', day: 'numeric' })
    }),
    datasets: [{
      label: 'Daily Revenue (₦)',
      data: Array.from({ length: 30 }, () => Math.floor(Math.random() * 50000) + 10000),
      borderColor: 'rgb(34, 197, 94)',
      backgroundColor: 'rgba(34, 197, 94, 0.1)',
      tension: 0.4
    }]
  }

  new Chart(ctx, {
    type: 'line',
    data: revenueData,
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

const createCashFlowChart = () => {
  if (!cashFlowChart.value) return

  const ctx = cashFlowChart.value.getContext('2d')
  
  // Mock data for demonstration
  const cashFlowData = {
    labels: ['Inflow', 'Outflow', 'Net Cash Flow'],
    datasets: [{
      data: [150000, 120000, 30000],
      backgroundColor: [
        'rgba(34, 197, 94, 0.8)',
        'rgba(239, 68, 68, 0.8)',
        'rgba(59, 130, 246, 0.8)'
      ],
      borderColor: [
        'rgb(34, 197, 94)',
        'rgb(239, 68, 68)',
        'rgb(59, 130, 246)'
      ],
      borderWidth: 1
    }]
  }

  new Chart(ctx, {
    type: 'doughnut',
    data: cashFlowData,
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'bottom'
        }
      }
    }
  })
}

const refreshAnalytics = async () => {
  await loadAnalyticsData()
  toast.success('Analytics data refreshed!')
}

const generateInsights = async () => {
  try {
    await analyticsApi.createBusinessInsight({
      title: 'AI Generated Insight',
      description: 'This is a sample AI-generated business insight based on your recent data patterns.',
      priority: 'medium',
      recommendations: [
        'Consider increasing inventory for top-selling products',
        'Optimize pricing strategy for better profit margins',
        'Focus on customer retention programs'
      ]
    })
    await loadAnalyticsData()
    toast.success('New insights generated!')
  } catch (error) {
    console.error('Failed to generate insights:', error)
  }
}

const markInsightViewed = async (insight) => {
  try {
    await analyticsApi.markInsightViewed(insight.id)
    insight.is_viewed = true
    toast.success('Insight marked as viewed!')
  } catch (error) {
    console.error('Failed to mark insight as viewed:', error)
  }
}

const rateInsight = async (insight) => {
  // TODO: Implement rating modal
  toast.info('Rating functionality coming soon!')
}

const toggleAlert = async (alert) => {
  try {
    await analyticsApi.updateAlertRule(alert.id, { is_active: !alert.is_active })
    alert.is_active = !alert.is_active
    toast.success(`Alert ${alert.is_active ? 'enabled' : 'disabled'}!`)
  } catch (error) {
    console.error('Failed to toggle alert:', error)
  }
}

onMounted(() => {
  loadAnalyticsData()
})
</script>
