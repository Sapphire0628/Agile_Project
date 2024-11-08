import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import Home from '../views/Home.vue'
import AddProject from '../views/AddProject.vue'
import Project from '../views/Project.vue'
import Team from '../views/Team.vue'

const routes = [
  {
    path: '/',
    redirect: '/login'  
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
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
// router.beforeEach((to, from, next) => {
//   const isAuthenticated = localStorage.getItem('token') // 假设使用token存储登录状态
  
//   if (to.meta.requiresAuth && !isAuthenticated) {
//     next('/login')
//   } else {
//     next()
//   }
// })

export default router 