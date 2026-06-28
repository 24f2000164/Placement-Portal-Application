import api from './api'

export default {
  async getDashboard() {
    const response = await api.get('/api/v1/company/dashboard')
    return response.data
  },

  async getProfile() {
    const response = await api.get('/api/v1/company/profile')
    return response.data
  },

  async updateProfile(data) {
    const response = await api.put('/api/v1/company/profile', data)
    return response.data
  },

  async getDrives() {
    const response = await api.get('/api/v1/company/drives')
    return response.data
  },

  async createDrive(data) {
    const response = await api.post('/api/v1/company/drives', data)
    return response.data
  },

  async updateDrive(id, data) {
    const response = await api.put('/api/v1/company/drives/' + id, data)
    return response.data
  },

  async closeDrive(id) {
    const response = await api.put('/api/v1/company/drives/' + id + '/close')
    return response.data
  },

  async getApplicants(driveId) {
    const response = await api.get('/api/v1/company/drives/' + driveId + '/applicants')
    return response.data
  },

  async updateApplicationStatus(applicationId, status, feedback) {
    const payload = {}
    if (status) payload.status = status
    if (feedback) payload.feedback = feedback
    const response = await api.put('/api/v1/company/applications/' + applicationId + '/status', payload)
    return response.data
  },

  async scheduleInterview(applicationId, data) {
    const response = await api.post('/api/v1/company/applications/' + applicationId + '/interview', data)
    return response.data
  },

  async getStudentProfile(studentId) {
    const response = await api.get('/api/v1/company/students/' + studentId)
    return response.data
  },

  async getAllApplications() {
    const response = await api.get('/api/v1/company/applications')
    return response.data
  },

  async triggerCsvExport() {
    const response = await api.post('/api/v1/company/export/csv')
    return response.data
  }
}