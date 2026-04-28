import api from './api'

export default {
  async loginUser(email, password) {
    const response = await api.post('/api/auth/login', { email, password })
    return response.data
  },

  async registerStudent(data) {
    const response = await api.post('/api/auth/register/student', data)
    return response.data
  },

  async registerCompany(data) {
    const response = await api.post('/api/auth/register/company', data)
    return response.data
  },

  async getMe() {
    const response = await api.get('/api/auth/me')
    return response.data
  }
}