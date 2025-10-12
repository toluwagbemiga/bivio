<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Inventory Management</h1>
        <p class="text-gray-600 mt-1">Manage your products and stock levels</p>
      </div>
      <div class="flex space-x-3">
        <button @click="showAddProduct = true" class="btn btn-primary">
          <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
          </svg>
          Add Product
        </button>
        <button @click="showAddCategory = true" class="btn btn-secondary">
          <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
          </svg>
          Add Category
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
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
              </svg>
            </div>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">Total Products</p>
            <p class="text-2xl font-semibold text-gray-900">{{ products.length }}</p>
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
            <p class="text-sm font-medium text-gray-500">Total Value</p>
            <p class="text-2xl font-semibold text-gray-900">₦{{ formatCurrency(totalInventoryValue) }}</p>
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
            <p class="text-2xl font-semibold text-gray-900">{{ lowStockProducts.length }}</p>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <div class="w-8 h-8 bg-red-100 rounded-lg flex items-center justify-center">
              <svg class="w-5 h-5 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </div>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">Out of Stock</p>
            <p class="text-2xl font-semibold text-gray-900">{{ outOfStockProducts.length }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Filters and Search -->
    <div class="card">
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-4 sm:space-y-0">
        <div class="flex flex-col sm:flex-row sm:items-center space-y-4 sm:space-y-0 sm:space-x-4">
          <div class="relative">
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Search products..."
              class="input pl-10"
            />
            <svg class="absolute left-3 top-3 h-4 w-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
          <select v-model="selectedCategory" class="input">
            <option value="">All Categories</option>
            <option v-for="category in categories" :key="category.id" :value="category.id">
              {{ category.name }}
            </option>
          </select>
          <select v-model="stockFilter" class="input">
            <option value="">All Stock Levels</option>
            <option value="low">Low Stock</option>
            <option value="out">Out of Stock</option>
            <option value="in_stock">In Stock</option>
          </select>
        </div>
        <div class="flex items-center space-x-2">
          <button @click="refreshProducts" class="btn btn-secondary">
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Refresh
          </button>
        </div>
      </div>
    </div>

    <!-- Products Table -->
    <div class="card">
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Product
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Category
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Stock
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Cost Price
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Selling Price
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
            <tr v-for="product in filteredProducts" :key="product.id">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                  <div class="w-10 h-10 bg-gray-100 rounded-lg flex items-center justify-center">
                    <svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
                    </svg>
                  </div>
                  <div class="ml-4">
                    <div class="text-sm font-medium text-gray-900">{{ product.name }}</div>
                    <div class="text-sm text-gray-500">{{ product.sku }}</div>
                  </div>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {{ product.category?.name || 'No Category' }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {{ product.current_stock }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                ₦{{ formatCurrency(product.cost_price) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                ₦{{ formatCurrency(product.selling_price) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="badge" :class="getStockStatusClass(product)">
                  {{ getStockStatus(product) }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                <div class="flex space-x-2">
                  <button @click="editProduct(product)" class="text-blue-600 hover:text-blue-900">
                    Edit
                  </button>
                  <button @click="adjustStock(product)" class="text-green-600 hover:text-green-900">
                    Adjust
                  </button>
                  <button @click="deleteProduct(product)" class="text-red-600 hover:text-red-900">
                    Delete
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Add Product Modal -->
    <div v-if="showAddProduct" class="fixed inset-0 z-50 overflow-hidden">
      <div class="absolute inset-0 bg-black bg-opacity-25" @click="showAddProduct = false"></div>
      <div class="absolute inset-0 flex items-center justify-center p-4">
        <div class="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
          <h3 class="text-lg font-medium text-gray-900 mb-4">Add New Product</h3>
          <form @submit.prevent="handleAddProduct">
            <div class="space-y-4">
              <div>
                <label class="label">Product Name</label>
                <input v-model="newProduct.name" type="text" required class="input" />
              </div>
              <div>
                <label class="label">SKU</label>
                <input v-model="newProduct.sku" type="text" required class="input" />
              </div>
              <div>
                <label class="label">Category</label>
                <select v-model="newProduct.category" required class="input">
                  <option value="">Select Category</option>
                  <option v-for="category in categories" :key="category.id" :value="category.id">
                    {{ category.name }}
                  </option>
                </select>
              </div>
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="label">Cost Price</label>
                  <input v-model="newProduct.cost_price" type="number" step="0.01" required class="input" />
                </div>
                <div>
                  <label class="label">Selling Price</label>
                  <input v-model="newProduct.selling_price" type="number" step="0.01" required class="input" />
                </div>
              </div>
              <div>
                <label class="label">Initial Stock</label>
                <input v-model="newProduct.current_stock" type="number" required class="input" />
              </div>
              <div>
                <label class="label">Minimum Stock Level</label>
                <input v-model="newProduct.minimum_stock_level" type="number" required class="input" />
              </div>
            </div>
            <div class="flex justify-end space-x-3 mt-6">
              <button type="button" @click="showAddProduct = false" class="btn btn-secondary">
                Cancel
              </button>
              <button type="submit" :disabled="isLoading" class="btn btn-primary">
                Add Product
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Add Category Modal -->
    <div v-if="showAddCategory" class="fixed inset-0 z-50 overflow-hidden">
      <div class="absolute inset-0 bg-black bg-opacity-25" @click="showAddCategory = false"></div>
      <div class="absolute inset-0 flex items-center justify-center p-4">
        <div class="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
          <h3 class="text-lg font-medium text-gray-900 mb-4">Add New Category</h3>
          <form @submit.prevent="handleAddCategory">
            <div class="space-y-4">
              <div>
                <label class="label">Category Name</label>
                <input v-model="newCategory.name" type="text" required class="input" />
              </div>
              <div>
                <label class="label">Description</label>
                <textarea v-model="newCategory.description" class="input" rows="3"></textarea>
              </div>
            </div>
            <div class="flex justify-end space-x-3 mt-6">
              <button type="button" @click="showAddCategory = false" class="btn btn-secondary">
                Cancel
              </button>
              <button type="submit" :disabled="isLoading" class="btn btn-primary">
                Add Category
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
import { useInventoryStore } from '../stores/inventory'
import { useToast } from 'vue-toastification'

const inventoryStore = useInventoryStore()
const toast = useToast()

const showAddProduct = ref(false)
const showAddCategory = ref(false)
const isLoading = ref(false)
const searchQuery = ref('')
const selectedCategory = ref('')
const stockFilter = ref('')

const newProduct = ref({
  name: '',
  sku: '',
  category: '',
  cost_price: '',
  selling_price: '',
  current_stock: '',
  minimum_stock_level: ''
})

const newCategory = ref({
  name: '',
  description: ''
})

const products = computed(() => inventoryStore.products)
const categories = computed(() => inventoryStore.categories)
const lowStockProducts = computed(() => inventoryStore.lowStockProducts)
const outOfStockProducts = computed(() => inventoryStore.outOfStockProducts)
const totalInventoryValue = computed(() => inventoryStore.totalInventoryValue)

const filteredProducts = computed(() => {
  let filtered = products.value

  if (searchQuery.value) {
    filtered = filtered.filter(product =>
      product.name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      product.sku.toLowerCase().includes(searchQuery.value.toLowerCase())
    )
  }

  if (selectedCategory.value) {
    filtered = filtered.filter(product => product.category?.id === selectedCategory.value)
  }

  if (stockFilter.value) {
    switch (stockFilter.value) {
      case 'low':
        filtered = filtered.filter(product => product.is_low_stock)
        break
      case 'out':
        filtered = filtered.filter(product => product.is_out_of_stock)
        break
      case 'in_stock':
        filtered = filtered.filter(product => !product.is_low_stock && !product.is_out_of_stock)
        break
    }
  }

  return filtered
})

const formatCurrency = (amount) => {
  return new Intl.NumberFormat('en-NG', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(amount)
}

const getStockStatus = (product) => {
  if (product.is_out_of_stock) return 'Out of Stock'
  if (product.is_low_stock) return 'Low Stock'
  return 'In Stock'
}

const getStockStatusClass = (product) => {
  if (product.is_out_of_stock) return 'badge-danger'
  if (product.is_low_stock) return 'badge-warning'
  return 'badge-success'
}

const refreshProducts = async () => {
  await inventoryStore.fetchProducts()
  await inventoryStore.fetchCategories()
}

const handleAddProduct = async () => {
  isLoading.value = true
  try {
    await inventoryStore.createProduct(newProduct.value)
    showAddProduct.value = false
    resetNewProduct()
  } catch (error) {
    console.error('Failed to add product:', error)
  } finally {
    isLoading.value = false
  }
}

const handleAddCategory = async () => {
  isLoading.value = true
  try {
    await inventoryStore.createCategory(newCategory.value)
    showAddCategory.value = false
    resetNewCategory()
  } catch (error) {
    console.error('Failed to add category:', error)
  } finally {
    isLoading.value = false
  }
}

const editProduct = (product) => {
  // TODO: Implement edit functionality
  toast.info('Edit functionality coming soon!')
}

const adjustStock = (product) => {
  // TODO: Implement stock adjustment
  toast.info('Stock adjustment coming soon!')
}

const deleteProduct = async (product) => {
  if (confirm(`Are you sure you want to delete ${product.name}?`)) {
    try {
      await inventoryStore.deleteProduct(product.id)
    } catch (error) {
      console.error('Failed to delete product:', error)
    }
  }
}

const resetNewProduct = () => {
  newProduct.value = {
    name: '',
    sku: '',
    category: '',
    cost_price: '',
    selling_price: '',
    current_stock: '',
    minimum_stock_level: ''
  }
}

const resetNewCategory = () => {
  newCategory.value = {
    name: '',
    description: ''
  }
}

onMounted(async () => {
  await refreshProducts()
})
</script>
