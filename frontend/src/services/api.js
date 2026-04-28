import axios from 'axios'

const api = axios.create({
  baseURL: process.env.VUE_APP_API_URL || 'http://localhost:5000',
  headers: {
    'Content-Type': 'application/json'
  }
})

api.interceptors.request.use(function(config) {
  const token = localStorage.getItem('token')
  if (token && token !== 'null' && token !== 'undefined') {
    config.headers['Authorization'] = 'Bearer ' + token
  }
  return config
})

api.interceptors.response.use(
  function(response) {
    return response
  },
  function(error) {
    if (error.response && error.response.status === 401) {
      const currentPath = window.location.pathname
      if (currentPath !== '/login' && currentPath !== '/register') {
        localStorage.removeItem('token')
        localStorage.removeItem('user')
        localStorage.removeItem('role')
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

export default api