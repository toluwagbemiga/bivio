import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'
import Toast from 'vue-toastification'
import 'vue-toastification/dist/index.css'

import App from './App.vue'
import './style.css'

// Import pages
import Login from './pages/Login.vue'
import Dashboard from './pages/Dashboard.vue'
import Inventory from './pages/Inventory.vue'
import Transactions from './pages/Transactions.vue'
import Loans from './pages/Loans.vue'
import Savings from './pages/Savings.vue'
import Analytics from './pages/Analytics.vue'
import Settings from './pages/Settings.vue'

// Import layouts
import MainLayout from './layouts/MainLayout.vue'
import AuthLayout from './layouts/AuthLayout.vue'

const routes = [
  {
    path: '/login',
    component: AuthLayout,
    children: [
      { path: '', component: Login }
    ]
  },
  {
    path: '/',
    component: MainLayout,
    children: [
      { path: '', component: Dashboard },
      { path: 'inventory', component: Inventory },
      { path: 'transactions', component: Transactions },
      { path: 'loans', component: Loans },
      { path: 'savings', component: Savings },
      { path: 'analytics', component: Analytics },
      { path: 'settings', component: Settings }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

const pinia = createPinia()

const app = createApp(App)

app.use(pinia)
app.use(router)
app.use(Toast, {
  position: 'top-right',
  timeout: 3000,
  closeOnClick: true,
  pauseOnFocusLoss: true,
  pauseOnHover: true,
  draggable: true,
  draggablePercent: 0.6,
  showCloseButtonOnHover: false,
  hideProgressBar: false,
  closeButton: 'button',
  icon: true,
  rtl: false
})

app.mount('#app')
