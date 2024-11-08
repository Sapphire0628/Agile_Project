const state = {
    token: localStorage.getItem('token') || '',
    username: localStorage.getItem('username') || ''
  }
  
  const mutations = {
    SET_TOKEN(state, token) {
      state.token = token
      localStorage.setItem('token', token)
    },
    REMOVE_TOKEN(state) {
      state.token = ''
      localStorage.removeItem('token')
    },
    SET_USERNAME(state, username) {
      state.username = username
      localStorage.setItem('username', username)
    }
  }
  
  const actions = {
    login({ commit }, token) {
      commit('SET_TOKEN', token)
    },
    logout({ commit }) {
      commit('REMOVE_TOKEN')
    },
    setUsername({ commit }, username) {
      commit('SET_USERNAME', username)
    }
  }

  const getters = {
    token: state => state.token,
    username: state => state.username
  }
  
  export default {
    namespaced: true,
    state,
    mutations,
    actions,
    getters
  }