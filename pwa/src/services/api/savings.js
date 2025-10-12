import api from './base'

export const savingsApi = {
  // Savings Accounts
  getSavingsAccounts: (params) => api.get('/savings/accounts/', { params }),
  getSavingsAccount: (id) => api.get(`/savings/accounts/${id}/`),
  createSavingsAccount: (accountData) => api.post('/savings/accounts/', accountData),
  updateSavingsAccount: (id, accountData) => api.put(`/savings/accounts/${id}/`, accountData),
  deleteSavingsAccount: (id) => api.delete(`/savings/accounts/${id}/`),
  getActiveAccounts: () => api.get('/savings/accounts/active/'),
  depositToAccount: (id, depositData) => api.post(`/savings/accounts/${id}/deposit/`, depositData),
  withdrawFromAccount: (id, withdrawalData) => api.post(`/savings/accounts/${id}/withdraw/`, withdrawalData),
  getAccountTransactions: (id, params) => api.get(`/savings/accounts/${id}/transactions/`, { params }),
  setDefaultAccount: (id) => api.post(`/savings/accounts/${id}/set_default/`),
  getDashboardStats: () => api.get('/savings/accounts/dashboard_stats/'),
  
  // Savings Transactions
  getSavingsTransactions: (params) => api.get('/savings/transactions/', { params }),
  getSavingsTransaction: (id) => api.get(`/savings/transactions/${id}/`),
  createSavingsTransaction: (transactionData) => api.post('/savings/transactions/', transactionData),
  updateSavingsTransaction: (id, transactionData) => api.put(`/savings/transactions/${id}/`, transactionData),
  deleteSavingsTransaction: (id) => api.delete(`/savings/transactions/${id}/`),
  getDeposits: () => api.get('/savings/transactions/deposits/'),
  getWithdrawals: () => api.get('/savings/transactions/withdrawals/'),
  getAutoSaves: () => api.get('/savings/transactions/auto_saves/'),
  getTodayTransactions: () => api.get('/savings/transactions/today/'),
  getTransactionSummary: (params) => api.get('/savings/transactions/summary/', { params }),
  
  // Savings Goals
  getSavingsGoals: (params) => api.get('/savings/goals/', { params }),
  getSavingsGoal: (id) => api.get(`/savings/goals/${id}/`),
  createSavingsGoal: (goalData) => api.post('/savings/goals/', goalData),
  updateSavingsGoal: (id, goalData) => api.put(`/savings/goals/${id}/`, goalData),
  deleteSavingsGoal: (id) => api.delete(`/savings/goals/${id}/`),
  getActiveGoals: () => api.get('/savings/goals/active/'),
  getCompletedGoals: () => api.get('/savings/goals/completed/'),
  contributeToGoal: (id, contributionData) => api.post(`/savings/goals/${id}/contribute/`, contributionData),
  pauseGoal: (id) => api.post(`/savings/goals/${id}/pause/`),
  resumeGoal: (id) => api.post(`/savings/goals/${id}/resume/`),
  getGoalsDashboardStats: () => api.get('/savings/goals/dashboard_stats/')
}
