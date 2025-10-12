import api from './base'

export const transactionApi = {
  // Transaction Categories
  getTransactionCategories: (params) => api.get('/transactions/categories/', { params }),
  getTransactionCategory: (id) => api.get(`/transactions/categories/${id}/`),
  createTransactionCategory: (categoryData) => api.post('/transactions/categories/', categoryData),
  updateTransactionCategory: (id, categoryData) => api.put(`/transactions/categories/${id}/`, categoryData),
  deleteTransactionCategory: (id) => api.delete(`/transactions/categories/${id}/`),
  getActiveTransactionCategories: () => api.get('/transactions/categories/active/'),
  getCategoryTransactions: (id) => api.get(`/transactions/categories/${id}/transactions/`),
  
  // Transactions
  getTransactions: (params) => api.get('/transactions/transactions/', { params }),
  getTransaction: (id) => api.get(`/transactions/transactions/${id}/`),
  createTransaction: (transactionData) => api.post('/transactions/transactions/', transactionData),
  updateTransaction: (id, transactionData) => api.put(`/transactions/transactions/${id}/`, transactionData),
  deleteTransaction: (id) => api.delete(`/transactions/transactions/${id}/`),
  getTodayTransactions: () => api.get('/transactions/transactions/today/'),
  getSalesTransactions: () => api.get('/transactions/transactions/sales/'),
  getPurchaseTransactions: () => api.get('/transactions/transactions/purchases/'),
  getDashboardStats: () => api.get('/transactions/transactions/dashboard_stats/'),
  getCashFlow: (params) => api.get('/transactions/transactions/cash_flow/', { params }),
  categorizeTransaction: (id, categoryData) => api.post(`/transactions/transactions/${id}/categorize/`, categoryData),
  refundTransaction: (id, refundData) => api.post(`/transactions/transactions/${id}/refund/`, refundData),
  bulkCategorizeTransactions: (bulkData) => api.post('/transactions/transactions/bulk_categorize/', bulkData),
  
  // Transaction Items
  getTransactionItems: (params) => api.get('/transactions/items/', { params }),
  getTransactionItem: (id) => api.get(`/transactions/items/${id}/`),
  createTransactionItem: (itemData) => api.post('/transactions/items/', itemData),
  updateTransactionItem: (id, itemData) => api.put(`/transactions/items/${id}/`, itemData),
  deleteTransactionItem: (id) => api.delete(`/transactions/items/${id}/`),
  getTopSellingItems: (params) => api.get('/transactions/items/top_selling/', { params }),
  getItemsByProduct: (productId) => api.get('/transactions/items/by_product/', { params: { product_id: productId } })
}
