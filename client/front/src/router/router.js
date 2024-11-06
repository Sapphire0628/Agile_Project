import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import Home from '../views/Home.vue'
import AddProject from '../views/AddProject.vue'

const routes = [
  {
    path: '/',
    redirect: '/login'  // 默认重定向到登录页
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: {
      requiresAuth: false  // 不需要登录验证
    }
  },
  {
    path: '/register',
    name: 'Register',
    component: Register,
    meta: {
      requiresAuth: false  // 不需要登录验证
    }
  },
  {
    path: '/home',
    name: 'Home',
    component: Home,
    // meta: {
    //   requiresAuth: true  // 需要登录验证
    // }
  },
  {
    path: '/add-project',
    name: 'AddProject',
    component: AddProject,
    meta: {
      requiresAuth: true  // 需要登录验证
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
router.beforeEach((to, from, next) => {
  console.log('Global navigation guard:', to.path)
  next()
})
export default router 