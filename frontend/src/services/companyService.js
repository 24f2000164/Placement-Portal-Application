import api from './api'

export default {
  async getDashboard() {
    const response = await api.get('/api/company/dashboard')
    return response.data
  },

  async getProfile() {
    const response = await api.get('/api/company/profile')
    return response.data
  },

  async updateProfile(data) {
    const response = await api.put('/api/company/profile', data)
    return response.data
  },

  async getDrives() {
    const response = await api.get('/api/company/drives')
    return response.data
  },

  async createDrive(data) {
    const response = await api.post('/api/company/drives', data)
    return response.data
  },

  async updateDrive(id, data) {
    const response = await api.put('/api/company/drives/' + id, data)
    return response.data
  },

  async closeDrive(id) {
    const response = await api.put('/api/company/drives/' + id + '/close')
    return response.data
  },

  async getApplicants(driveId) {
    const response = await api.get('/api/company/drives/' + driveId + '/applicants')
    return response.data
  },

  async updateApplicationStatus(applicationId, status, feedback) {
    const payload = {}
    if (status) payload.status = status
    if (feedback) payload.feedback = feedback
    const response = await api.put('/api/company/applications/' + applicationId + '/status', payload)
    return response.data
  },

  async scheduleInterview(applicationId, data) {
    const response = await api.post('/api/company/applications/' + applicationId + '/interview', data)
    return response.data
  },

  async getStudentProfile(studentId) {
    const response = await api.get('/api/company/students/' + studentId)
    return response.data
  },

  async getAllApplications() {
    const response = await api.get('/api/company/applications')
    return response.data
  },

  async triggerCsvExport() {
    const response = await api.post('/api/company/export/csv')
    return response.data
  }
}