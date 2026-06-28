import api from './api'

export default {
  async getPublicStats() {
    const response = await api.get('/api/v1/public/stats')
    return response.data
  },

  async getPublicTrends() {
    const response = await api.get('/api/v1/public/monthly-trends')
    return response.data
  },

  async getAdminOverview() {
    const response = await api.get('/api/v1/analytics/admin/overview')
    return response.data
  },

  async getCompanyOverview() {
    const response = await api.get('/api/v1/analytics/company/overview')
    return response.data
  },

  async getStudentOverview() {
    const response = await api.get('/api/v1/analytics/student/overview')
    return response.data
  }
}