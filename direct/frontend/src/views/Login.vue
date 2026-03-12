<template>
  <div class="auth-container">
    <div class="logo">
      <i class="ri-twitter-x-line"></i>
      <h1>Twitter Clone</h1>
    </div>
    <div class="auth-card">
      <h2>登录</h2>
      <p class="subtitle">欢迎回来！</p>
      <div class="form-group">
        <label>用户名或邮箱</label>
        <input type="text" v-model="username" placeholder="请输入用户名或邮箱">
      </div>
      <div class="form-group">
        <label>密码</label>
        <input type="password" v-model="password" placeholder="请输入密码" @keyup.enter="login">
      </div>
      <button class="btn" @click="login" :disabled="loading">
        {{ loading ? '登录中...' : '登录' }}
      </button>
      <p class="switch-auth">
        还没有账号？<a href="#/register">立即注册</a>
      </p>
    </div>
    <div class="toast" :class="{ show: showToast }">{{ toastMessage }}</div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'

const router = useRouter()
const username = ref('')
const password = ref('')
const loading = ref(false)
const showToast = ref(false)
const toastMessage = ref('')

const showToastMessage = (msg) => {
  toastMessage.value = msg
  showToast.value = true
  setTimeout(() => {
    showToast.value = false
  }, 3000)
}

const login = async () => {
  if (!username.value || !password.value) {
    showToastMessage('请填写完整信息')
    return
  }

  loading.value = true
  try {
    const response = await axios.post('/api/login', {
      username: username.value,
      password: password.value
    })

    if (response.data.success) {
      localStorage.setItem('user', JSON.stringify(response.data.user))
      localStorage.setItem('token', response.data.token || '')
      router.push('/index')
    } else {
      showToastMessage(response.data.message || '登录失败')
    }
  } catch (error) {
    showToastMessage(error.response?.data?.message || '登录失败，请稍后重试')
  } finally {
    loading.value = false
  }
}
</script>