import { createApp } from 'vue'
import App from './App.vue'
import 'vuetify/styles'
import { library } from '@fortawesome/fontawesome-svg-core'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import { fas } from '@fortawesome/free-solid-svg-icons'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import router from './router/router.js'
import '@fortawesome/fontawesome-free/css/all.css';
import '@mdi/font/css/materialdesignicons.css';
import axios from 'axios'
import store from './store'
import { aliases, mdi } from 'vuetify/iconsets/mdi'
library.add(fas)

const vuetify = createVuetify({
    components,
    directives,
    icons: {
        defaultSet: 'mdi',
        aliases,
        sets: {
            mdi
        }
    }
})
const app = createApp(App)
app.config.globalProperties.$axios = axios
axios.interceptors.request.use(
    (config) => {
      // 从 Vuex 获取 Token
      const token = store.getters['user/getToken'];
      
      if (token) {
        // 设置 Authorization 请求头
        config.headers['Authorization'] = `Bearer ${token}`;
      }
  
      return config;
    },
    (error) => {
      return Promise.reject(error);
    }
  );

  const token = localStorage.getItem('token');
  if (token) {
    store.dispatch('user/login', token); // 将 Token 存入 Vuex
  } 

app.component('font-awesome-icon', FontAwesomeIcon)
app.use(store)
app.use(vuetify)
app.use(router)
app.mount('#app')

