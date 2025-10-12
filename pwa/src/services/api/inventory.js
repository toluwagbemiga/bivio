import api from './base'

export const inventoryApi = {
  // Categories
  getCategories: (params) => api.get('/inventory/categories/', { params }),
  getCategory: (id) => api.get(`/inventory/categories/${id}/`),
  createCategory: (categoryData) => api.post('/inventory/categories/', categoryData),
  updateCategory: (id, categoryData) => api.put(`/inventory/categories/${id}/`, categoryData),
  deleteCategory: (id) => api.delete(`/inventory/categories/${id}/`),
  getActiveCategories: () => api.get('/inventory/categories/active/'),
  getCategoryProducts: (id) => api.get(`/inventory/categories/${id}/products/`),
  getCategoryStats: (id) => api.get(`/inventory/categories/${id}/stats/`),
  
  // Products
  getProducts: (params) => api.get('/inventory/products/', { params }),
  getProduct: (id) => api.get(`/inventory/products/${id}/`),
  createProduct: (productData) => api.post('/inventory/products/', productData),
  updateProduct: (id, productData) => api.put(`/inventory/products/${id}/`, productData),
  deleteProduct: (id) => api.delete(`/inventory/products/${id}/`),
  getLowStockProducts: () => api.get('/inventory/products/low_stock/'),
  getOutOfStockProducts: () => api.get('/inventory/products/out_of_stock/'),
  getTopSellingProducts: (params) => api.get('/inventory/products/top_selling/', { params }),
  getSlowMovingProducts: (params) => api.get('/inventory/products/slow_moving/', { params }),
  adjustStock: (id, adjustmentData) => api.post(`/inventory/products/${id}/adjust_stock/`, adjustmentData),
  restockProduct: (id, restockData) => api.post(`/inventory/products/${id}/restock/`, restockData),
  getStockHistory: (id) => api.get(`/inventory/products/${id}/stock_history/`),
  getDashboardStats: () => api.get('/inventory/products/dashboard_stats/'),
  
  // Stock Movements
  getStockMovements: (params) => api.get('/inventory/stock-movements/', { params }),
  getStockMovement: (id) => api.get(`/inventory/stock-movements/${id}/`),
  createStockMovement: (movementData) => api.post('/inventory/stock-movements/', movementData),
  updateStockMovement: (id, movementData) => api.put(`/inventory/stock-movements/${id}/`, movementData),
  deleteStockMovement: (id) => api.delete(`/inventory/stock-movements/${id}/`),
  getTodayMovements: () => api.get('/inventory/stock-movements/today/'),
  getMovementsByType: (type) => api.get('/inventory/stock-movements/by_type/', { params: { type } }),
  getMovementSummary: (params) => api.get('/inventory/stock-movements/summary/', { params })
} 