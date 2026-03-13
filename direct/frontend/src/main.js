import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import axios from 'axios'
import './assets/styles.css'

// 配置 axios 携带 Cookie
axios.defaults.withCredentials = true

createApp(App).use(router).mount('#app')