import api from './base'

export const loanApi = {
  // Loan Products
  getLoanProducts: (params) => api.get('/loans/products/', { params }),
  getLoanProduct: (id) => api.get(`/loans/products/${id}/`),
  createLoanProduct: (productData) => api.post('/loans/products/', productData),
  updateLoanProduct: (id, productData) => api.put(`/loans/products/${id}/`, productData),
  deleteLoanProduct: (id) => api.delete(`/loans/products/${id}/`),
  getAvailableLoanProducts: () => api.get('/loans/products/available/'),
  calculateLoan: (id, calculationData) => api.post(`/loans/products/${id}/calculate_loan/`, calculationData),
  
  // Loans
  getLoans: (params) => api.get('/loans/loans/', { params }),
  getLoan: (id) => api.get(`/loans/loans/${id}/`),
  createLoan: (loanData) => api.post('/loans/loans/', loanData),
  updateLoan: (id, loanData) => api.put(`/loans/loans/${id}/`, loanData),
  deleteLoan: (id) => api.delete(`/loans/loans/${id}/`),
  getMyLoans: () => api.get('/loans/loans/my_loans/'),
  getActiveLoans: () => api.get('/loans/loans/active/'),
  getOverdueLoans: () => api.get('/loans/loans/overdue/'),
  approveLoan: (id, approvalData) => api.post(`/loans/loans/${id}/approve/`, approvalData),
  rejectLoan: (id, rejectionData) => api.post(`/loans/loans/${id}/reject/`, rejectionData),
  disburseLoan: (id) => api.post(`/loans/loans/${id}/disburse/`),
  getLoanRepayments: (id) => api.get(`/loans/loans/${id}/repayments/`),
  makeLoanPayment: (id, paymentData) => api.post(`/loans/loans/${id}/make_payment/`, paymentData),
  getDashboardStats: () => api.get('/loans/loans/dashboard_stats/'),
  
  // Loan Repayments
  getRepayments: (params) => api.get('/loans/repayments/', { params }),
  getRepayment: (id) => api.get(`/loans/repayments/${id}/`),
  createRepayment: (repaymentData) => api.post('/loans/repayments/', repaymentData),
  updateRepayment: (id, repaymentData) => api.put(`/loans/repayments/${id}/`, repaymentData),
  deleteRepayment: (id) => api.delete(`/loans/repayments/${id}/`),
  getPendingRepayments: () => api.get('/loans/repayments/pending/'),
  getOverdueRepayments: () => api.get('/loans/repayments/overdue/'),
  processRepayment: (id, processData) => api.post(`/loans/repayments/${id}/process_payment/`, processData)
}
