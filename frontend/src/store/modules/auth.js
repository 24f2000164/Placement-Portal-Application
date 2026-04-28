import authService from '@/services/authService'

const state = {
  token: localStorage.getItem('token') || null,
  user: (function() {
    try {
      return JSON.parse(localStorage.getItem('user')) || null
    } catch (e) {
      return null
    }
  })(),
  role: localStorage.getItem('role') || null
}

const getters = {
  isLoggedIn: function(state) {
    return !!state.token && state.token !== 'null' && state.token !== 'undefined'
  },
  currentUser: function(state) {
    return state.user
  },
  userRole: function(state) {
    return state.role
  }
}

const mutations = {
  SET_AUTH(state, payload) {
    state.token = payload.token
    state.user = payload.user
    state.role = payload.role
    localStorage.setItem('token', payload.token)
    localStorage.setItem('user', JSON.stringify(payload.user))
    localStorage.setItem('role', payload.role)

    console.log("✅ TOKEN SAVED:", payload.token)

  },
  CLEAR_AUTH(state) {


    console.log("❌ CLEAR_AUTH CALLED")

    console.trace("WHO CALLED LOGOUT")  // 🔥 VERY IMPORTANT
    state.token = null
    state.user = null
    state.role = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    localStorage.removeItem('role')
  }
}

const actions = {
  async login({ commit }, { email, password }) {
    const data = await authService.loginUser(email, password)
    console.log("Login success") 
    
    commit('SET_AUTH', {
      token: data.token,
      role: data.role,
      user: {  email: data.email, role: data.role }
    })
    return data.role
  },

  async registerStudent({ commit }, formData) {
    const data = await authService.registerStudent(formData)
    return data
  },

  async registerCompany({ commit }, formData) {
    const data = await authService.registerCompany(formData)
    return data
  },

  logout({ commit }) {
    commit('CLEAR_AUTH')
  }
}

export default {
  namespaced: true,
  state,
  getters,
  mutations,
  actions
}