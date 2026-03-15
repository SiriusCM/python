import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import axios from 'axios'
import './assets/styles.css'

// 配置 axios 携带 Cookie
axios.defaults.withCredentials = true

// 动态推断 API 基础路径
// 在 Hash 模式下，location.pathname 就是项目的基准路径（如 /wjzgTest/ 或 /）
// 我们直接使用它作为 Axios 的 baseURL，去掉末尾斜杠即可
let apiBase = location.pathname
if (apiBase !== '/' && apiBase.endsWith('/')) {
  apiBase = apiBase.slice(0, -1)
}

// 如果不是根路径，则设置 baseURL
if (apiBase !== '' && apiBase !== '/') {
  axios.defaults.baseURL = apiBase
}

createApp(App).use(router).mount('#app')