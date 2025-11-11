import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Threat API
export const threatApi = {
  getThreats: (params?: any) => api.get('/threats/', { params }),
  getThreat: (id: string) => api.get(`/threats/${id}`),
  getStats: (days: number = 7) => api.get('/threats/stats', { params: { days } }),
  updateThreat: (id: string, data: any) => api.patch(`/threats/${id}`, data),
  deleteThreat: (id: string) => api.delete(`/threats/${id}`),
  searchThreats: (query: string) => api.post('/threats/search', null, { params: { query } }),
}

// Monitoring Rules API
export const rulesApi = {
  getRules: () => api.get('/rules/'),
  getRule: (id: string) => api.get(`/rules/${id}`),
  createRule: (data: any) => api.post('/rules/', data),
  updateRule: (id: string, data: any) => api.patch(`/rules/${id}`, data),
  deleteRule: (id: string) => api.delete(`/rules/${id}`),
  toggleRule: (id: string) => api.post(`/rules/${id}/toggle`),
}

export default api
