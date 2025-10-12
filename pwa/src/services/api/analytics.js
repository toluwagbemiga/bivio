import api from './base'

export const analyticsApi = {
  // Business Metrics
  getBusinessMetrics: (params) => api.get('/analytics/metrics/', { params }),
  getBusinessMetric: (id) => api.get(`/analytics/metrics/${id}/`),
  createBusinessMetric: (metricData) => api.post('/analytics/metrics/', metricData),
  updateBusinessMetric: (id, metricData) => api.put(`/analytics/metrics/${id}/`, metricData),
  deleteBusinessMetric: (id) => api.delete(`/analytics/metrics/${id}/`),
  getDashboard: () => api.get('/analytics/metrics/dashboard/'),
  generateMetrics: (generationData) => api.post('/analytics/metrics/generate_metrics/', generationData),
  getPerformanceTrends: (params) => api.get('/analytics/metrics/performance_trends/', { params }),
  
  // Cash Flow Data
  getCashFlowData: (params) => api.get('/analytics/cash-flow/', { params }),
  getCashFlowDatum: (id) => api.get(`/analytics/cash-flow/${id}/`),
  createCashFlowDatum: (cashFlowData) => api.post('/analytics/cash-flow/', cashFlowData),
  updateCashFlowDatum: (id, cashFlowData) => api.put(`/analytics/cash-flow/${id}/`, cashFlowData),
  deleteCashFlowDatum: (id) => api.delete(`/analytics/cash-flow/${id}/`),
  getCashFlowSummary: (params) => api.get('/analytics/cash-flow/summary/', { params }),
  generateFromTransactions: (generationData) => api.post('/analytics/cash-flow/generate_from_transactions/', generationData),
  
  // Business Insights
  getBusinessInsights: (params) => api.get('/analytics/insights/', { params }),
  getBusinessInsight: (id) => api.get(`/analytics/insights/${id}/`),
  createBusinessInsight: (insightData) => api.post('/analytics/insights/', insightData),
  updateBusinessInsight: (id, insightData) => api.put(`/analytics/insights/${id}/`, insightData),
  deleteBusinessInsight: (id) => api.delete(`/analytics/insights/${id}/`),
  getUnreadInsights: () => api.get('/analytics/insights/unread/'),
  getHighPriorityInsights: () => api.get('/analytics/insights/high_priority/'),
  markInsightViewed: (id) => api.post(`/analytics/insights/${id}/mark_viewed/`),
  markInsightImplemented: (id, implementationData) => api.post(`/analytics/insights/${id}/mark_implemented/`, implementationData),
  rateInsight: (id, ratingData) => api.post(`/analytics/insights/${id}/rate/`, ratingData),
  
  // Alert Rules
  getAlertRules: (params) => api.get('/analytics/alerts/', { params }),
  getAlertRule: (id) => api.get(`/analytics/alerts/${id}/`),
  createAlertRule: (ruleData) => api.post('/analytics/alerts/', ruleData),
  updateAlertRule: (id, ruleData) => api.put(`/analytics/alerts/${id}/`, ruleData),
  deleteAlertRule: (id) => api.delete(`/analytics/alerts/${id}/`),
  getActiveAlertRules: () => api.get('/analytics/alerts/active/'),
  testAlertRule: (id, testData) => api.post(`/analytics/alerts/${id}/test/`, testData),
  triggerAlertRule: (id) => api.post(`/analytics/alerts/${id}/trigger/`)
}
