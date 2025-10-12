import api from './base'

export const aiApi = {
  // Category Predictions
  getCategoryPredictions: (params) => api.get('/ai/predictions/', { params }),
  getCategoryPrediction: (id) => api.get(`/ai/predictions/${id}/`),
  createCategoryPrediction: (predictionData) => api.post('/ai/predictions/', predictionData),
  updateCategoryPrediction: (id, predictionData) => api.put(`/ai/predictions/${id}/`, predictionData),
  deleteCategoryPrediction: (id) => api.delete(`/ai/predictions/${id}/`),
  predictCategory: (predictionData) => api.post('/ai/predictions/predict/', predictionData),
  provideFeedback: (id, feedbackData) => api.post(`/ai/predictions/${id}/provide_feedback/`, feedbackData),
  getAccuracyStats: () => api.get('/ai/predictions/accuracy_stats/'),
  getRecentPredictions: (params) => api.get('/ai/predictions/recent_predictions/', { params }),
  
  // Training Data
  getTrainingData: (params) => api.get('/ai/training-data/', { params }),
  getTrainingDatum: (id) => api.get(`/ai/training-data/${id}/`),
  createTrainingDatum: (trainingData) => api.post('/ai/training-data/', trainingData),
  updateTrainingDatum: (id, trainingData) => api.put(`/ai/training-data/${id}/`, trainingData),
  deleteTrainingDatum: (id) => api.delete(`/ai/training-data/${id}/`),
  getValidatedTrainingData: () => api.get('/ai/training-data/validated/'),
  getTrainingDataByCategory: (categoryId) => api.get('/ai/training-data/by_category/', { params: { category_id: categoryId } }),
  validateTrainingDatum: (id, validationData) => api.post(`/ai/training-data/${id}/validate/`, validationData),
  getTrainingDataStats: () => api.get('/ai/training-data/stats/'),
  
  // Model Performance
  getModelPerformance: (params) => api.get('/ai/model-performance/', { params }),
  getModelPerformanceRecord: (id) => api.get(`/ai/model-performance/${id}/`),
  getCurrentModel: () => api.get('/ai/model-performance/current_model/'),
  getPerformanceHistory: () => api.get('/ai/model-performance/performance_history/')
}
