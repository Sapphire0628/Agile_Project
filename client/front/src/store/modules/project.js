const state = {
    workingProjects: [],
    ownedProjects: [],
    loading: false,
    error: null
  }
  
  const mutations = {
    SET_WORKING_PROJECTS(state, projects) {
      state.workingProjects = projects
    },
    SET_OWNED_PROJECTS(state, projects) {
      state.ownedProjects = projects
    },
    SET_LOADING(state, status) {
      state.loading = status
    },
    SET_ERROR(state, error) {
      state.error = error
    },
    REMOVE_PROJECT(state, projectId) {
      state.ownedProjects = state.ownedProjects.filter(
        project => project.project_id !== projectId
      )
      state.workingProjects = state.workingProjects.filter(
        project => project.project_id !== projectId
      )
    }
  }
  
  const getters = {
    getWorkingProjects: state => state.workingProjects,
    getOwnedProjects: state => state.ownedProjects,
    isLoading: state => state.loading,
    getError: state => state.error
  }
  
  export default {
    namespaced: true,
    state,
    mutations,
    getters
  }