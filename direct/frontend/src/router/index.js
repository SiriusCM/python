import { createRouter, createWebHashHistory } from 'vue-router'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import Index from '../views/Index.vue'
import CreatePost from '../views/CreatePost.vue'

const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login', name: 'Login', component: Login },
  { path: '/register', name: 'Register', component: Register },
  { path: '/index', name: 'Index', component: Index },
  { path: '/create', name: 'CreatePost', component: CreatePost }
]

const router = createRouter({
  // 使用 Hash 模式，无需关心部署路径
  history: createWebHashHistory(),
  routes
})

export default router