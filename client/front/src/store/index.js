import { createStore } from 'vuex'
import user from './modules/user'
import project from './modules/project'
export default createStore({
  modules: {
    user,
    project
  }
})