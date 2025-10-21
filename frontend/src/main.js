import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import axios from 'axios'

// Configure axios to use credentials (cookies) for all requests
axios.defaults.withCredentials = true

// Make axios available globally as $http
const app = createApp(App)
app.config.globalProperties.$http = axios
app.use(router)
app.mount('#app')
