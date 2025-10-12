import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { transactionApi } from '../services/api/transactions'
import { useToast } from 'vue-toastification'

export const useTransactionStore = defineStore('transactions', () => {
  const transactions = ref([])
  const categories = ref([])
  const items = ref([])
  const isLoading = ref(false)
  const toast = useToast()

  const todayTransactions = computed(() => 
    transactions.value.filter(t => {
      const today = new Date().toDateString()
      return new Date(t.transaction_date).toDateString() === today
    })
  )

  const salesTransactions = computed(() => 
    transactions.value.filter(t => t.transaction_type === 'sale')
  )

  const purchaseTransactions = computed(() => 
    transactions.value.filter(t => t.transaction_type === 'purchase')
  )

  const totalSalesToday = computed(() => 
    todayTransactions.value
      .filter(t => t.transaction_type === 'sale')
      .reduce((total, t) => total + parseFloat(t.total_amount), 0)
  )

  const fetchTransactions = async (params = {}) => {
    isLoading.value = true
    try {
      const response = await transactionApi.getTransactions(params)
      transactions.value = response.results || response
      return response
    } catch (error) {
      toast.error('Failed to fetch transactions')
      throw error
    } finally {
      isLoading.value = false
    }
  }

  const fetchCategories = async () => {
    try {
      const response = await transactionApi.getTransactionCategories()
      categories.value = response.results || response
      return response
    } catch (error) {
      toast.error('Failed to fetch transaction categories')
      throw error
    }
  }

  const createTransaction = async (transactionData) => {
    try {
      const newTransaction = await transactionApi.createTransaction(transactionData)
      transactions.value.unshift(newTransaction)
      toast.success('Transaction created successfully!')
      return newTransaction
    } catch (error) {
      toast.error(error.message || 'Failed to create transaction')
      throw error
    }
  }

  const updateTransaction = async (id, transactionData) => {
    try {
      const updatedTransaction = await transactionApi.updateTransaction(id, transactionData)
      const index = transactions.value.findIndex(t => t.id === id)
      if (index !== -1) {
        transactions.value[index] = updatedTransaction
      }
      toast.success('Transaction updated successfully!')
      return updatedTransaction
    } catch (error) {
      toast.error(error.message || 'Failed to update transaction')
      throw error
    }
  }

  const categorizeTransaction = async (id, categoryId) => {
    try {
      const updatedTransaction = await transactionApi.categorizeTransaction(id, { category_id: categoryId })
      const index = transactions.value.findIndex(t => t.id === id)
      if (index !== -1) {
        transactions.value[index] = updatedTransaction
      }
      toast.success('Transaction categorized successfully!')
      return updatedTransaction
    } catch (error) {
      toast.error(error.message || 'Failed to categorize transaction')
      throw error
    }
  }

  const refundTransaction = async (id, refundData) => {
    try {
      const refundTransaction = await transactionApi.refundTransaction(id, refundData)
      transactions.value.unshift(refundTransaction)
      toast.success('Refund processed successfully!')
      return refundTransaction
    } catch (error) {
      toast.error(error.message || 'Failed to process refund')
      throw error
    }
  }

  const getDashboardStats = async () => {
    try {
      const stats = await transactionApi.getDashboardStats()
      return stats
    } catch (error) {
      toast.error('Failed to fetch dashboard stats')
      throw error
    }
  }

  const getCashFlow = async (params = {}) => {
    try {
      const cashFlow = await transactionApi.getCashFlow(params)
      return cashFlow
    } catch (error) {
      toast.error('Failed to fetch cash flow data')
      throw error
    }
  }

  return {
    transactions,
    categories,
    items,
    isLoading,
    todayTransactions,
    salesTransactions,
    purchaseTransactions,
    totalSalesToday,
    fetchTransactions,
    fetchCategories,
    createTransaction,
    updateTransaction,
    categorizeTransaction,
    refundTransaction,
    getDashboardStats,
    getCashFlow
  }
})
