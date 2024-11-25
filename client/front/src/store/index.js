import { createStore } from 'vuex'
import user from './modules/user'
import project from './modules/project'

const store = createStore({
  modules: {
    user,
    project
  }
})

export default store