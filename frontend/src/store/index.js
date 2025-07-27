import { createStore } from 'vuex'
import axios from 'axios'

export default createStore({
  state: {
    token: localStorage.getItem('token') || null,
    user: JSON.parse(localStorage.getItem('user')) || null,
    isAuthenticated: false,
    serverStatus: 'online',
    notifications: []
  },
  mutations: {
    setToken(state, token) {
      state.token = token
      state.isAuthenticated = !!token
      if (token) {
        localStorage.setItem('token', token)
        axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
      } else {
        localStorage.removeItem('token')
        delete axios.defaults.headers.common['Authorization']
      }
    },
    setUser(state, user) {
      state.user = user
      if (user) {
        localStorage.setItem('user', JSON.stringify(user))
      } else {
        localStorage.removeItem('user')
      }
    },
    clearAuth(state) {
      state.token = null
      state.user = null
      state.isAuthenticated = false
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      delete axios.defaults.headers.common['Authorization']
    },
    setServerStatus(state, status) {
      state.serverStatus = status
    },
    addNotification(state, notification) {
      state.notifications.push({
        id: Date.now(),
        ...notification,
        timestamp: new Date()
      })
    },
    removeNotification(state, notificationId) {
      state.notifications = state.notifications.filter(n => n.id !== notificationId)
    }
  },
  actions: {
    async login({ commit }, credentials) {
      try {
        const params = new URLSearchParams()
        params.append('username', credentials.username)
        params.append('password', credentials.password)

        const response = await axios.post('/api/auth/token', params, {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
        })

        const token = response.data.access_token
        commit('setToken', token)

        // Decode token to get user info
        const payload = JSON.parse(atob(token.split('.')[1]))
        commit('setUser', { 
          username: payload.sub, 
          isAdmin: payload.is_admin 
        })

        return { success: true, user: payload }
      } catch (error) {
        commit('clearAuth')
        throw error
      }
    },

    logout({ commit }) {
      commit('clearAuth')
    },

    initializeAuth({ commit, state }) {
      if (state.token) {
        axios.defaults.headers.common['Authorization'] = `Bearer ${state.token}`
        commit('setToken', state.token) // This will set isAuthenticated
      }
    },

    showNotification({ commit }, notification) {
      commit('addNotification', notification)
      
      // Auto-remove notification after 5 seconds
      setTimeout(() => {
        commit('removeNotification', notification.id || Date.now())
      }, 5000)
    }
  },
  getters: {
    isAuthenticated: state => state.isAuthenticated,
    isAdmin: state => state.user?.isAdmin || false,
    currentUser: state => state.user,
    serverStatus: state => state.serverStatus,
    notifications: state => state.notifications
  },
  modules: {
  }
})
