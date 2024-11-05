<template>
    <Register/> 
</template>

<script>
import router from './router/router'
import Login from './components/Login.vue'
import Register from './components/Register.vue'

export default {
  name: 'App',
  components: {
    Login,
    Register
  }
}
</script>

<style>
</style>