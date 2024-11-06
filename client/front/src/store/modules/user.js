const state = {
    token: localStorage.getItem('token') || ''
  }
  
  const mutations = {
    SET_TOKEN(state, token) {
      state.token = token
      // 同时存入 localStorage
      localStorage.setItem('token', token)
    },
    REMOVE_TOKEN(state) {
      state.token = ''
      // 同时从 localStorage 移除
      localStorage.removeItem('token')
    }
  }
  
  const actions = {
    // 登录成功后保存 token
    login({ commit }, token) {
      commit('SET_TOKEN', token)
    },
    // 登出时清除 token  
    logout({ commit }) {
      commit('REMOVE_TOKEN')
    }
  }

  const getters = {
    token: state => state.token
  }
  
  export default {
    namespaced: true,
    state,
    mutations,
    actions,
    getters
  }