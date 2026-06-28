import api from './api'

export default {
  async getDashboardStats() {
    const response = await api.get('/api/v1/admin/dashboard')
    return response.data
  },

  async getAllCompanies() {
    const response = await api.get('/api/v1/admin/companies')
    return response.data
  },

  async getAllStudents() {
    const response = await api.get('/api/v1/admin/students')
    return response.data
  },

  async getAllDrives() {
    const response = await api.get('/api/v1/admin/drives')
    return response.data
  },

  async getAllApplications() {
    const response = await api.get('/api/v1/admin/applications')
    return response.data
  },

  async approveCompany(id) {
    const response = await api.put('/api/v1/admin/companies/' + id + '/approve')
    return response.data
  },

  async rejectCompany(id) {
    const response = await api.put('/api/v1/admin/companies/' + id + '/reject')
    return response.data
  },

  async blacklistCompany(id) {
    const response = await api.put('/api/v1/admin/companies/' + id + '/blacklist')
    return response.data
  },

  async unblacklistCompany(id) {
    const response = await api.put('/api/v1/admin/companies/' + id + '/unblacklist')
    return response.data
  },

  async blacklistStudent(id) {
    const response = await api.put('/api/v1/admin/students/' + id + '/blacklist')
    return response.data
  },

  async unblacklistStudent(id) {
    const response = await api.put('/api/v1/admin/students/' + id + '/unblacklist')
    return response.data
  },

  async approveDrive(id) {
    const response = await api.put('/api/v1/admin/drives/' + id + '/approve')
    return response.data
  },

  async rejectDrive(id) {
    const response = await api.put('/api/v1/admin/drives/' + id + '/reject')
    return response.data
  },

  async searchCompanies(query, name = '', industry = '') {
    const params = new URLSearchParams()
    if (query)    params.append('q', query)
    if (name)     params.append('name', name)
    if (industry) params.append('industry', industry)
    const response = await api.get('/api/v1/admin/search/companies?' + params.toString())
    return response.data
  },

  async searchStudents(query) {
    const response = await api.get('/api/v1/admin/search/students?q=' + query)
    return response.data
  },

  async getLogs() {
    const response = await api.get('/api/v1/admin/logs')
    return response.data
  },

  async getStudentDetail(id) {
    const response = await api.get('/api/v1/admin/students/' + id)
    return response.data
  },

  async getCompanyDetail(id) {
    const response = await api.get('/api/v1/admin/companies/' + id)
    return response.data
  },

  async getReports() {
    const response = await api.get('/api/v1/admin/reports')
    return response.data
  },

  async triggerReport() {
    const response = await api.post('/api/v1/admin/reports/generate')
    return response.data
  }
}