const state = {
    workingProjects: [],
    ownedProjects: [],
    currentProjectId: localStorage.getItem('currentProjectId') || null,
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
    SET_CURRENT_PROJECT_ID(state, projectId) {
      state.currentProjectId = projectId
      if (projectId) {
        localStorage.setItem('currentProjectId', projectId)
      } else {
        localStorage.removeItem('currentProjectId')
      }
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
    getError: state => state.error,
    getCurrentProjectId: state => state.currentProjectId,
  }

  
  export default {
    namespaced: true,
    state,
    mutations,
    getters
  }