import { createApp } from 'vue'
import App from './App.vue'
import 'vuetify/styles'
import { library } from '@fortawesome/fontawesome-svg-core'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import { fas } from '@fortawesome/free-solid-svg-icons'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import router from './router/router'
import '@fortawesome/fontawesome-free/css/all.css';
import axios from 'axios'

library.add(fas)

const vuetify = createVuetify({
    components,
    directives,
    icons: {
        iconfont: 'fa'
    }
})
const app = createApp(App)
app.config.globalProperties.$axios = axios
app.component('font-awesome-icon', FontAwesomeIcon)
app.use(vuetify)
app.use(router)
app.mount('#app')

