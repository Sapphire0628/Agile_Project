const state = {
    token: localStorage.getItem('token') || '',
    username: localStorage.getItem('username') || '',
  }
  
  const mutations = {
    SET_TOKEN(state, token) {
      state.token = token
      localStorage.setItem('token', token)
    },

    SET_USERNAME(state, username) {
      state.username = username
      localStorage.setItem('username', username)
    },
    CLEAR_USER_STATE(state) {
      state.token = null
      state.username = null
      localStorage.removeItem('token')
      localStorage.removeItem('username')
    }
  }
  
  const actions = {
    login({ commit }, token) {
      commit('SET_TOKEN', token)
    },
    logout({ commit }) {
      commit('CLEAR_USER_STATE')
    },
    setUsername({ commit }, username) {
      commit('SET_USERNAME', username)
    }
  }

  const getters = {
    token: state => state.token,
    username: state => state.username,
    isAuthenticated: state => !!state.token
  }
  
  export default {
    namespaced: true,
    state,
    mutations,
    actions,
    getters
  }