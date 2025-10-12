import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { inventoryApi } from '../services/api/inventory'
import { useToast } from 'vue-toastification'

export const useInventoryStore = defineStore('inventory', () => {
  const products = ref([])
  const categories = ref([])
  const stockMovements = ref([])
  const isLoading = ref(false)
  const toast = useToast()

  const lowStockProducts = computed(() => 
    products.value.filter(product => product.is_low_stock)
  )

  const outOfStockProducts = computed(() => 
    products.value.filter(product => product.is_out_of_stock)
  )

  const totalInventoryValue = computed(() => 
    products.value.reduce((total, product) => 
      total + (product.current_stock * product.cost_price), 0
    )
  )

  const fetchProducts = async (params = {}) => {
    isLoading.value = true
    try {
      const response = await inventoryApi.getProducts(params)
      products.value = response.results || response
      return response
    } catch (error) {
      toast.error('Failed to fetch products')
      throw error
    } finally {
      isLoading.value = false
    }
  }

  const fetchCategories = async () => {
    try {
      const response = await inventoryApi.getCategories()
      categories.value = response.results || response
      return response
    } catch (error) {
      toast.error('Failed to fetch categories')
      throw error
    }
  }

  const createProduct = async (productData) => {
    try {
      const newProduct = await inventoryApi.createProduct(productData)
      products.value.unshift(newProduct)
      toast.success('Product created successfully!')
      return newProduct
    } catch (error) {
      toast.error(error.message || 'Failed to create product')
      throw error
    }
  }

  const updateProduct = async (id, productData) => {
    try {
      const updatedProduct = await inventoryApi.updateProduct(id, productData)
      const index = products.value.findIndex(p => p.id === id)
      if (index !== -1) {
        products.value[index] = updatedProduct
      }
      toast.success('Product updated successfully!')
      return updatedProduct
    } catch (error) {
      toast.error(error.message || 'Failed to update product')
      throw error
    }
  }

  const deleteProduct = async (id) => {
    try {
      await inventoryApi.deleteProduct(id)
      products.value = products.value.filter(p => p.id !== id)
      toast.success('Product deleted successfully!')
    } catch (error) {
      toast.error(error.message || 'Failed to delete product')
      throw error
    }
  }

  const adjustStock = async (id, adjustmentData) => {
    try {
      const updatedProduct = await inventoryApi.adjustStock(id, adjustmentData)
      const index = products.value.findIndex(p => p.id === id)
      if (index !== -1) {
        products.value[index] = updatedProduct
      }
      toast.success('Stock adjusted successfully!')
      return updatedProduct
    } catch (error) {
      toast.error(error.message || 'Failed to adjust stock')
      throw error
    }
  }

  const restockProduct = async (id, restockData) => {
    try {
      const updatedProduct = await inventoryApi.restockProduct(id, restockData)
      const index = products.value.findIndex(p => p.id === id)
      if (index !== -1) {
        products.value[index] = updatedProduct
      }
      toast.success('Product restocked successfully!')
      return updatedProduct
    } catch (error) {
      toast.error(error.message || 'Failed to restock product')
      throw error
    }
  }

  const fetchStockMovements = async (params = {}) => {
    try {
      const response = await inventoryApi.getStockMovements(params)
      stockMovements.value = response.results || response
      return response
    } catch (error) {
      toast.error('Failed to fetch stock movements')
      throw error
    }
  }

  const getDashboardStats = async () => {
    try {
      const stats = await inventoryApi.getDashboardStats()
      return stats
    } catch (error) {
      toast.error('Failed to fetch dashboard stats')
      throw error
    }
  }

  return {
    products,
    categories,
    stockMovements,
    isLoading,
    lowStockProducts,
    outOfStockProducts,
    totalInventoryValue,
    fetchProducts,
    fetchCategories,
    createProduct,
    updateProduct,
    deleteProduct,
    adjustStock,
    restockProduct,
    fetchStockMovements,
    getDashboardStats
  }
})
