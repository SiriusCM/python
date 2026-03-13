<template>
  <div class="create-post-container">
    <!-- 顶部导航 -->
    <header class="header">
      <span class="back-btn" @click="goBack">
        <i class="ri-arrow-left-line"></i>
      </span>
      <h1>发帖</h1>
      <button class="btn btn-small" :disabled="!canPost" @click="submitPost">发布</button>
    </header>

    <div class="post-editor">
      <div class="post-user-info">
        <img :src="currentUser?.avatar || defaultAvatar" alt="头像" class="user-avatar">
        <span class="username">@{{ currentUser?.username }}</span>
      </div>

      <textarea
        class="post-textarea"
        v-model="postContent"
        placeholder="有什么新鲜事想分享给大家？"
        maxlength="500"
        @input="updateCharCount"
        ref="textareaRef"
      ></textarea>

      <div class="char-count" :class="{ warning: charCount > 450 }">{{ charCount }}/500</div>

      <!-- 图片预览 -->
      <div class="image-preview-container" v-if="images.length > 0">
        <div v-for="(img, index) in images" :key="index" class="image-preview-item">
          <img :src="img" alt="预览">
          <span class="remove-image" @click="removeImage(index)">
            <i class="ri-close-line"></i>
          </span>
        </div>
      </div>

      <!-- 上传图片按钮 -->
      <div class="upload-actions">
        <label class="upload-btn" for="imageInput">
          <i class="ri-image-line"></i>
          <span>图片</span>
        </label>
        <input type="file" id="imageInput" accept="image/*" multiple style="display: none;" @change="handleImageUpload">
      </div>
    </div>

    <!-- Toast -->
    <div class="toast" :class="{ show: showToast }">{{ toastMessage }}</div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const defaultAvatar = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="50" cy="50" r="50" fill="%23667eea"/></svg>'

const currentUser = ref(null)
const postContent = ref('')
const charCount = ref(0)
const images = ref([])
const showToast = ref(false)
const toastMessage = ref('')
const textareaRef = ref(null)

const canPost = computed(() => {
  return postContent.value.trim().length > 0 || images.value.length > 0
})

const getAuthHeader = () => {
  const token = localStorage.getItem('token')
  return token ? { 'Authorization': `Bearer ${token}` } : {}
}

const showToastMessage = (msg) => {
  toastMessage.value = msg
  showToast.value = true
  setTimeout(() => {
    showToast.value = false
  }, 3000)
}

const goBack = () => {
  router.back()
}

const updateCharCount = () => {
  charCount.value = postContent.value.length
}

const handleImageUpload = (e) => {
  const files = e.target.files
  if (!files) return

  for (let i = 0; i < files.length; i++) {
    const file = files[i]
    if (file.size > 5 * 1024 * 1024) {
      showToastMessage('图片不能超过5MB')
      continue
    }

    const reader = new FileReader()
    reader.onload = (e) => {
      images.value.push(e.target.result)
    }
    reader.readAsDataURL(file)
  }

  // 清空input以允许再次选择相同文件
  e.target.value = ''
}

const removeImage = (index) => {
  images.value.splice(index, 1)
}

const submitPost = async () => {
  if (!canPost.value) {
    showToastMessage('请输入内容或上传图片')
    return
  }

  try {
    const formData = new FormData()
    formData.append('content', postContent.value)

    // 添加图片
    for (const [index, img] of images.value.entries()) {
      // 将base64转为Blob
      const base64Response = await fetch(img)
      const blob = await base64Response.blob()
      const file = new File([blob], `image_${index}.jpg`, { type: 'image/jpeg' })
      formData.append('images', file)
    }

    const response = await axios.post('/api/posts/create', formData, {
      headers: {
        ...getAuthHeader(),
        'Content-Type': 'multipart/form-data'
      }
    })

    if (response.data.success) {
      showToastMessage('发布成功')
      setTimeout(() => {
        router.push('/index')
      }, 1000)
    } else {
      showToastMessage(response.data.message || '发布失败')
    }
  } catch (error) {
    showToastMessage(error.response?.data?.message || '发布失败')
  }
}

onMounted(() => {
  const user = localStorage.getItem('user')
  if (!user) {
    router.push('/login')
    return
  }

  currentUser.value = JSON.parse(user)

  // 自动聚焦到输入框
  if (textareaRef.value) {
    textareaRef.value.focus()
  }
})
</script>

<style scoped>
.create-post-container {
  min-height: 100vh;
  background: rgba(26, 26, 46, 0.95);
}

.header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 60px;
  background: rgba(26, 26, 46, 0.9);
  backdrop-filter: blur(20px);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
  z-index: 1000;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.header h1 {
  font-size: 18px;
  font-weight: 700;
  color: white;
}

.header .back-btn {
  font-size: 24px;
  color: white;
  cursor: pointer;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-small {
  width: auto;
  padding: 8px 20px;
  font-size: 14px;
  background: linear-gradient(135deg, #1da1f2, #0d8ecf);
  color: white;
  border: none;
  border-radius: 20px;
  cursor: pointer;
  font-weight: 600;
}

.btn-small:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.post-editor {
  padding: 80px 16px 20px;
  max-width: 600px;
  margin: 0 auto;
}

.post-user-info {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
}

.user-avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  margin-right: 12px;
  border: 2px solid rgba(255, 255, 255, 0.2);
}

.username {
  color: rgba(255, 255, 255, 0.7);
  font-size: 14px;
}

.post-textarea {
  width: 100%;
  min-height: 200px;
  background: transparent;
  border: none;
  color: white;
  font-size: 18px;
  line-height: 1.6;
  resize: none;
  outline: none;
}

.post-textarea::placeholder {
  color: rgba(255, 255, 255, 0.4);
}

.char-count {
  text-align: right;
  color: rgba(255, 255, 255, 0.5);
  font-size: 14px;
  margin-top: 8px;
}

.char-count.warning {
  color: #f4212e;
}

.image-preview-container {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 16px;
}

.image-preview-item {
  position: relative;
  width: 100px;
  height: 100px;
  border-radius: 12px;
  overflow: hidden;
}

.image-preview-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.remove-image {
  position: absolute;
  top: 4px;
  right: 4px;
  width: 24px;
  height: 24px;
  background: rgba(0, 0, 0, 0.7);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  cursor: pointer;
}

.upload-actions {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.upload-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  color: white;
  cursor: pointer;
  transition: all 0.3s;
}

.upload-btn:hover {
  background: rgba(255, 255, 255, 0.15);
}

.upload-btn i {
  font-size: 20px;
  color: #1da1f2;
}

/* Toast */
.toast {
  position: fixed;
  top: 20px;
  left: 50%;
  transform: translateX(-50%) translateY(-100px);
  background: rgba(255, 255, 255, 0.95);
  color: #333;
  padding: 12px 24px;
  border-radius: 12px;
  font-size: 14px;
  z-index: 3000;
  opacity: 0;
  transition: all 0.3s;
}

.toast.show {
  opacity: 1;
  transform: translateX(-50%) translateY(0);
}
</style>