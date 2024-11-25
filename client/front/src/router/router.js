import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import Home from '../views/Home.vue'
import AddProject from '../views/AddProject.vue'
import Project from '../views/Project.vue'
import Team from '../views/Team.vue'
import TaskDetail from '../views/TaskDetail.vue'
import SprintDashboard from '../views/SprintDashboard.vue'
import store from '../store'

const routes = [
  {
    path: '/',
    redirect: '/home'  
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: {
      requiresAuth: false  
    }
  },
  {
    path: '/register',
    name: 'Register',
    component: Register,
    meta: {
      requiresAuth: false 
    }
  },
  {
    path: '/home',
    name: 'Home',
    component: Home,
    meta: {
      requiresAuth: true  
    }
  },
  {
    path: '/add-project',
    name: 'AddProject',
    component: AddProject,
    meta: {
      requiresAuth: true  
    }
  },
  {
    path: '/project/:id',
    name: 'Project',
    component: Project,
    meta: {
      requiresAuth: true  
    }
  },
  {
    path:'/project/:id/team',
    name:'Team',
    component: Team,
    meta: {
      requiresAuth: true  
    }
  },
  {
    path: '/tasks/:id',
    name: 'TaskDetail',
    component: TaskDetail,
    props: true
  },
  {
    path: '/project/:id/:sprintName/:sprintId',
    name: 'SprintDashboard',
    component: SprintDashboard,
    meta: {
      requiresAuth: true
    }
  }

]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const isAuthenticated = store.getters['user/isAuthenticated']
  
  if (to.meta.requiresAuth && !isAuthenticated) {
    next({
      path: '/login',
      query: { redirect: to.fullPath }
    })
  } else if ((to.path === '/login' || to.path === '/register') && isAuthenticated) {
    next('/home')
  } else if (to.query.redirect && isAuthenticated) {
    next(to.query.redirect)
  } else {
    next()
  }
})

export default router 