<template>
  <div class="auth-container">
    <div class="logo">
      <i class="ri-twitter-x-line"></i>
      <h1>Twitter Clone</h1>
    </div>
    <div class="auth-card">
      <h2>注册</h2>
      <p class="subtitle">创建你的账号</p>
      <div class="form-group">
        <label>用户名</label>
        <input type="text" v-model="username" placeholder="请输入用户名">
      </div>
      <div class="form-group">
        <label>邮箱</label>
        <input type="email" v-model="email" placeholder="请输入邮箱">
      </div>
      <div class="form-group">
        <label>昵称（可选）</label>
        <input type="text" v-model="nickname" placeholder="请输入昵称">
      </div>
      <div class="form-group">
        <label>密码</label>
        <input type="password" v-model="password" placeholder="请输入密码" @keyup.enter="register">
      </div>
      <button class="btn" @click="register" :disabled="loading">
        {{ loading ? '注册中...' : '注册' }}
      </button>
      <p class="switch-auth">
        已有账号？<router-link to="/login">立即登录</router-link>
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
const email = ref('')
const nickname = ref('')
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

const register = async () => {
  if (!username.value || !email.value || !password.value) {
    showToastMessage('请填写完整信息')
    return
  }

  loading.value = true
  try {
    const response = await axios.post('/api/register', {
      username: username.value,
      email: email.value,
      nickname: nickname.value,
      password: password.value
    })

    if (response.data.success) {
      showToastMessage('注册成功，请登录')
      setTimeout(() => {
        router.push('/login')
      }, 1500)
    } else {
      showToastMessage(response.data.message || '注册失败')
    }
  } catch (error) {
    showToastMessage(error.response?.data?.message || '注册失败，请稍后重试')
  } finally {
    loading.value = false
  }
}
</script>