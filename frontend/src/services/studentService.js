import api from './api'

export default {
  async getProfile() {
    const response = await api.get('/api/v1/student/profile')
    return response.data
  },

  async updateProfile(data) {
    const response = await api.put('/api/v1/student/profile', data)
    return response.data
  },

  async uploadResume(file) {
    const formData = new FormData()
    formData.append('resume', file)
    const response = await api.post('/api/v1/student/resume', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    return response.data
  },

  async getDrives(params) {
    const query = new URLSearchParams()
    if (params && params.search) query.append('search', params.search)
    if (params && params.branch) query.append('branch', params.branch)
    if (params && params.min_cgpa) query.append('min_cgpa', params.min_cgpa)
    const response = await api.get('/api/v1/student/drives?' + query.toString())
    return response.data
  },

  async getDriveDetail(id) {
    const response = await api.get('/api/v1/student/drives/' + id)
    return response.data
  },

  async applyToDrive(driveId) {
    const response = await api.post('/api/v1/student/apply/' + driveId)
    return response.data
  },

  async getMyApplications() {
    const response = await api.get('/api/v1/student/applications')
    return response.data
  },

  async getHistory() {
    const response = await api.get('/api/v1/student/history')
    return response.data
  },

  async getApplicationTimeline(applicationId) {
    const response = await api.get('/api/v1/student/applications/' + applicationId + '/timeline')
    return response.data
  },

  async triggerCsvExport() {
    const response = await api.post('/api/v1/student/export/csv')
    return response.data
  },

  async downloadConfirmation(applicationId) {
    const response = await api.get('/api/v1/student/confirmation/' + applicationId, {
      responseType: 'blob'
    })
    const url = URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.download = 'confirmation_' + applicationId + '.txt'
    link.click()
    URL.revokeObjectURL(url)
  }
}