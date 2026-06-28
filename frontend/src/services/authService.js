import api from './api'

export default {
  async loginUser(email, password) {
    const response = await api.post('/api/v1/auth/login', { email, password })
    return response.data
  },

  async registerStudent(data) {
    const response = await api.post('/api/v1/auth/register/student', data)
    return response.data
  },

  async registerCompany(data) {
    const response = await api.post('/api/v1/auth/register/company', data)
    return response.data
  },

  async getMe() {
    const response = await api.get('/api/v1/auth/me')
    return response.data
  }
}