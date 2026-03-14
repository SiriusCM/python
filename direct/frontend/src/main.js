import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import axios from 'axios'
import './assets/styles.css'

// 配置 axios 携带 Cookie
axios.defaults.withCredentials = true

// 动态设置 API 基础路径
// 如果在 /wjzgTest/ 下运行，API 请求前缀加上 /wjzgTest
if (location.pathname.startsWith('/wjzgTest')) {
  axios.defaults.baseURL = '/wjzgTest'
}

createApp(App).use(router).mount('#app')