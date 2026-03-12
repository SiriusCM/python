<template>
  <div class="app-container">
    <!-- 顶部导航 -->
    <header class="header" v-if="currentUser">
      <span class="back-btn" @click="goBack" v-show="showBackBtn">
        <i class="ri-arrow-left-line"></i>
      </span>
      <h1>{{ headerTitle }}</h1>
    </header>

    <div class="page-container">
      <!-- 首页（Feed） -->
      <div v-show="currentPage === 'feed'" class="feed-page">
        <div v-for="post in feedPosts" :key="post.id" class="post-item" @click="viewProfile(post.user_id)">
          <div class="post-avatar">
            <img :src="post.user?.avatar || defaultAvatar" alt="头像">
          </div>
          <div class="post-content">
            <div class="post-header">
              <span class="post-nickname">{{ post.user?.nickname || post.user?.username }}</span>
              <span class="post-username">@{{ post.user?.username }}</span>
              <span class="post-time">{{ formatTime(post.created_at) }}</span>
            </div>
            <div class="post-text" @click.stop="viewPostDetail(post)">{{ post.content }}</div>
            <div class="post-actions" @click.stop>
              <button class="post-action" @click="toggleLike(post)">
                <i :class="[post.is_liked ? 'ri-heart-fill' : 'ri-heart-line', { liked: post.is_liked }]"></i>
                {{ post.likes_count || 0 }}
              </button>
              <button class="post-action" @click="viewPostDetail(post)">
                <i class="ri-chat-1-line"></i>
                {{ post.comments_count || 0 }}
              </button>
              <button class="post-action">
                <i class="ri-share-forward-line"></i>
              </button>
            </div>
          </div>
        </div>
        <div v-if="feedPosts.length === 0" class="empty-state">
          <i class="ri-bubble-chart-line"></i>
          <p>暂无动态，快来关注一些用户吧</p>
        </div>
        <div class="load-more" @click="loadMoreFeed" v-if="hasMoreFeed">加载更多</div>
      </div>

      <!-- 搜索页 -->
      <div v-show="currentPage === 'search'" class="search-page">
        <div class="search-input-wrapper">
          <i class="ri-search-line"></i>
          <input type="text" v-model="searchKeyword" placeholder="搜索用户" @input="searchUsers">
        </div>
        <div class="suggestions-section" v-if="!searchKeyword && suggestions.length > 0">
          <h3>推荐关注</h3>
          <div v-for="user in suggestions" :key="user.id" class="suggestion-item" @click="viewProfile(user.id)">
            <img :src="user.avatar || defaultAvatar" alt="头像">
            <div class="suggestion-item-info">
              <div class="suggestion-item-name">{{ user.nickname || user.username }}</div>
              <div class="suggestion-item-username">@{{ user.username }}</div>
            </div>
            <button class="btn" style="width: auto; padding: 6px 16px; font-size: 13px;" @click.stop="followUser(user)" v-if="!user.is_following">
              关注
            </button>
          </div>
        </div>
        <div v-if="searchResults.length > 0">
          <div v-for="user in searchResults" :key="user.id" class="user-item" @click="viewProfile(user.id)">
            <div class="user-item-avatar">
              <img :src="user.avatar || defaultAvatar" alt="头像">
            </div>
            <div>
              <div class="user-item-name">{{ user.nickname || user.username }}</div>
              <div class="user-item-username">@{{ user.username }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 用户资料页 -->
      <div v-show="currentPage === 'profile'" class="profile-page">
        <div class="profile-header">
          <div class="profile-banner"></div>
          <div class="profile-info">
            <div class="profile-avatar">
              <img :src="profileUser?.avatar || defaultAvatar" alt="头像">
            </div>
            <div class="profile-name">{{ profileUser?.nickname || profileUser?.username }}</div>
            <div class="profile-username">@{{ profileUser?.username }}</div>
            <div class="profile-bio" v-if="profileUser?.bio">{{ profileUser.bio }}</div>
            <div class="profile-stats">
              <span @click="showFollowingList">
                <strong>{{ profileUser?.following_count || 0 }}</strong> <span class="count-label">关注</span>
              </span>
              <span @click="showFollowersList">
                <strong>{{ profileUser?.follower_count || 0 }}</strong> <span class="count-label">粉丝</span>
              </span>
              <span>
                <strong>{{ profileUser?.post_count || 0 }}</strong> <span class="count-label">帖子</span>
              </span>
            </div>
            <div class="profile-actions" v-if="!isMyProfile">
              <button class="btn" @click="followUser(profileUser)" v-if="!profileUser?.is_following">
                关注
              </button>
              <button class="btn btn-outline" @click="unfollowUser(profileUser)" v-else>
                取消关注
              </button>
            </div>
          </div>
        </div>
        <div v-for="post in userPosts" :key="post.id" class="post-item">
          <div class="post-avatar">
            <img :src="post.user?.avatar || defaultAvatar" alt="头像">
          </div>
          <div class="post-content">
            <div class="post-header">
              <span class="post-nickname">{{ post.user?.nickname || post.user?.username }}</span>
              <span class="post-username">@{{ post.user?.username }}</span>
              <span class="post-time">{{ formatTime(post.created_at) }}</span>
            </div>
            <div class="post-text">{{ post.content }}</div>
            <div class="post-actions">
              <button class="post-action" @click="toggleLike(post)">
                <i :class="[post.is_liked ? 'ri-heart-fill' : 'ri-heart-line', { liked: post.is_liked }]"></i>
                {{ post.likes_count || 0 }}
              </button>
              <button class="post-action">
                <i class="ri-chat-1-line"></i>
                {{ post.comments_count || 0 }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- 个人中心页 -->
      <div v-show="currentPage === 'me'" class="profile-page">
        <div class="profile-header">
          <div class="profile-banner"></div>
          <div class="profile-info">
            <div class="profile-avatar">
              <img :src="currentUser?.avatar || defaultAvatar" alt="头像">
            </div>
            <div class="profile-name">{{ currentUser?.nickname || currentUser?.username }}</div>
            <div class="profile-username">@{{ currentUser?.username }}</div>
            <div class="profile-bio" v-if="currentUser?.bio">{{ currentUser.bio }}</div>
            <div class="profile-stats">
              <span @click="showMyFollowingList">
                <strong>{{ currentUser?.following_count || 0 }}</strong> <span class="count-label">关注</span>
              </span>
              <span @click="showMyFollowersList">
                <strong>{{ currentUser?.follower_count || 0 }}</strong> <span class="count-label">粉丝</span>
              </span>
              <span>
                <strong>{{ currentUser?.post_count || 0 }}</strong> <span class="count-label">帖子</span>
              </span>
            </div>
            <div class="profile-actions">
              <button class="btn btn-outline" @click="currentPage = 'editProfile'">编辑资料</button>
              <button class="btn btn-danger" @click="logout">退出登录</button>
            </div>
          </div>
        </div>
        <div v-for="post in myPosts" :key="post.id" class="post-item">
          <div class="post-avatar">
            <img :src="currentUser?.avatar || defaultAvatar" alt="头像">
          </div>
          <div class="post-content">
            <div class="post-header">
              <span class="post-nickname">{{ currentUser?.nickname || currentUser?.username }}</span>
              <span class="post-username">@{{ currentUser?.username }}</span>
              <span class="post-time">{{ formatTime(post.created_at) }}</span>
            </div>
            <div class="post-text">{{ post.content }}</div>
            <div class="post-actions">
              <button class="post-action" @click="toggleLike(post)">
                <i :class="[post.is_liked ? 'ri-heart-fill' : 'ri-heart-line', { liked: post.is_liked }]"></i>
                {{ post.likes_count || 0 }}
              </button>
              <button class="post-action">
                <i class="ri-chat-1-line"></i>
                {{ post.comments_count || 0 }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- 编辑资料页 -->
      <div v-show="currentPage === 'editProfile'" class="edit-profile-page">
        <div class="edit-avatar">
          <img :src="editForm.avatar || defaultAvatar" alt="头像">
          <div>
            <label for="avatarInput">更换头像</label>
            <input type="file" id="avatarInput" accept="image/*" style="display: none;" @change="handleAvatarChange">
          </div>
        </div>
        <div class="form-group">
          <label>昵称</label>
          <input type="text" v-model="editForm.nickname" placeholder="请输入昵称">
        </div>
        <div class="form-group">
          <label>个人简介</label>
          <input type="text" v-model="editForm.bio" placeholder="介绍一下自己">
        </div>
        <button class="btn" @click="saveProfile">保存</button>
      </div>

      <!-- 关注列表页 -->
      <div v-show="currentPage === 'following'" class="list-page">
        <div v-for="user in followingList" :key="user.id" class="user-item" @click="viewProfile(user.id)">
          <div class="user-item-avatar">
            <img :src="user.avatar || defaultAvatar" alt="头像">
          </div>
          <div>
            <div class="user-item-name">{{ user.nickname || user.username }}</div>
            <div class="user-item-username">@{{ user.username }}</div>
          </div>
        </div>
        <div v-if="followingList.length === 0" class="empty-state">
          <p>暂无关注</p>
        </div>
      </div>

      <!-- 粉丝列表页 -->
      <div v-show="currentPage === 'followers'" class="list-page">
        <div v-for="user in followersList" :key="user.id" class="user-item" @click="viewProfile(user.id)">
          <div class="user-item-avatar">
            <img :src="user.avatar || defaultAvatar" alt="头像">
          </div>
          <div>
            <div class="user-item-name">{{ user.nickname || user.username }}</div>
            <div class="user-item-username">@{{ user.username }}</div>
          </div>
        </div>
        <div v-if="followersList.length === 0" class="empty-state">
          <p>暂无粉丝</p>
        </div>
      </div>
    </div>

    <!-- 底部导航 -->
    <nav class="tabbar" v-if="currentUser">
      <button class="tabbar-item" :class="{ active: currentPage === 'feed' }" @click="switchPage('feed')">
        <i class="ri-home-5-line"></i>
        <span>首页</span>
      </button>
      <button class="tabbar-item" :class="{ active: currentPage === 'search' }" @click="switchPage('search')">
        <i class="ri-search-line"></i>
        <span>发现</span>
      </button>
      <button class="tabbar-item" :class="{ active: currentPage === 'me' }" @click="switchPage('me')">
        <i class="ri-user-line"></i>
        <span>我的</span>
      </button>
    </nav>

    <!-- 发帖按钮 -->
    <button class="fab" v-if="currentUser && currentPage !== 'editProfile' && currentPage !== 'following' && currentPage !== 'followers'" @click="showPostModal = true">
      <i class="ri-edit-line"></i>
    </button>

    <!-- 发帖弹窗 -->
    <div class="modal" :class="{ active: showPostModal }" @click="closePostModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <span class="close-btn" @click="showPostModal = false">
            <i class="ri-close-line"></i>
          </span>
          <button class="btn" style="width: auto; padding: 8px 20px;" @click="submitPost">发布</button>
        </div>
        <textarea class="post-textarea" v-model="postContent" placeholder="有什么新鲜事想分享给大家？" maxlength="500" @input="updateCharCount"></textarea>
        <div class="post-char-count">{{ charCount }}/500</div>
      </div>
    </div>

    <!-- Toast -->
    <div class="toast" :class="{ show: showToast }">{{ toastMessage }}</div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

const defaultAvatar = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="50" cy="50" r="50" fill="%23667eea"/></svg>'

// 状态
const currentUser = ref(null)
const currentPage = ref('feed')
const headerTitle = ref('首页')
const showBackBtn = ref(false)
const feedPage = ref(1)
const hasMoreFeed = ref(true)

// 搜索
const searchKeyword = ref('')
const searchResults = ref([])
const suggestions = ref([])

// 发帖
const showPostModal = ref(false)
const postContent = ref('')
const charCount = ref(0)

// 用户资料
const profileUser = ref(null)
const userPosts = ref([])
const myPosts = ref([])
const isMyProfile = ref(false)

// 编辑资料
const editForm = ref({
  nickname: '',
  bio: '',
  avatar: ''
})

// 列表
const followingList = ref([])
const followersList = ref([])

// Toast
const showToast = ref(false)
const toastMessage = ref('')

// 计算属性
const feedPosts = ref([])
const pageHistory = ref([])

// 方法
const showToastMessage = (msg) => {
  toastMessage.value = msg
  showToast.value = true
  setTimeout(() => {
    showToast.value = false
  }, 3000)
}

const formatTime = (time) => {
  if (!time) return ''
  const date = new Date(time)
  const now = new Date()
  const diff = (now - date) / 1000

  if (diff < 60) return '刚刚'
  if (diff < 3600) return Math.floor(diff / 60) + '分钟前'
  if (diff < 86400) return Math.floor(diff / 3600) + '小时前'
  if (diff < 604800) return Math.floor(diff / 86400) + '天前'
  return date.toLocaleDateString()
}

const switchPage = (page) => {
  if (page === currentPage.value) return

  if (['feed', 'search', 'me'].includes(currentPage.value)) {
    pageHistory.value.push(currentPage.value)
  }

  currentPage.value = page
  showBackBtn.value = !['feed', 'search', 'me'].includes(page)

  const titles = {
    feed: '首页',
    search: '发现',
    me: '我的',
    profile: '资料',
    editProfile: '编辑资料',
    following: '关注',
    followers: '粉丝'
  }
  headerTitle.value = titles[page] || '首页'

  if (page === 'feed') loadFeed()
  if (page === 'search') loadSuggestions()
  if (page === 'me') loadMyProfile()
}

const goBack = () => {
  if (pageHistory.value.length > 0) {
    currentPage.value = pageHistory.value.pop()
    showBackBtn.value = !['feed', 'search', 'me'].includes(currentPage.value)

    const titles = {
      feed: '首页',
      search: '发现',
      me: '我的'
    }
    headerTitle.value = titles[currentPage.value] || '首页'
  } else {
    switchPage('feed')
  }
}

const viewProfile = async (userId) => {
  try {
    const user = JSON.parse(localStorage.getItem('user') || '{}')
    isMyProfile.value = user.id === userId

    const response = await axios.get(`/api/users/${userId}`)
    profileUser.value = response.data.user

    const postsResponse = await axios.get(`/api/users/${userId}/posts`)
    userPosts.value = postsResponse.data.posts || []

    switchPage('profile')
  } catch (error) {
    showToastMessage('加载失败')
  }
}

const loadFeed = async () => {
  try {
    const response = await axios.get(`/api/feed?page=${feedPage.value}`)
    if (feedPage.value === 1) {
      feedPosts.value = response.data.posts || []
    } else {
      feedPosts.value.push(...(response.data.posts || []))
    }
    hasMoreFeed.value = response.data.has_more !== false
  } catch (error) {
    console.error('加载动态失败:', error)
  }
}

const loadMoreFeed = () => {
  feedPage.value++
  loadFeed()
}

const loadSuggestions = async () => {
  try {
    const response = await axios.get('/api/suggestions')
    suggestions.value = response.data.users || []
  } catch (error) {
    console.error('加载推荐失败:', error)
  }
}

const searchUsers = async () => {
  if (!searchKeyword.value.trim()) {
    searchResults.value = []
    return
  }

  try {
    const response = await axios.get(`/api/search?keyword=${searchKeyword.value}`)
    searchResults.value = response.data.users || []
  } catch (error) {
    console.error('搜索失败:', error)
  }
}

const loadMyProfile = async () => {
  try {
    const userData = JSON.parse(localStorage.getItem('user') || '{}')
    currentUser.value = userData

    const response = await axios.get(`/api/users/${userData.id}`)
    currentUser.value = response.data.user

    const postsResponse = await axios.get(`/api/users/${userData.id}/posts`)
    myPosts.value = postsResponse.data.posts || []
  } catch (error) {
    console.error('加载失败:', error)
  }
}

const followUser = async (user) => {
  try {
    await axios.post('/api/follow', { user_id: user.id })
    user.is_following = true
    user.follower_count = (user.follower_count || 0) + 1
    showToastMessage('关注成功')
  } catch (error) {
    showToastMessage(error.response?.data?.message || '关注失败')
  }
}

const unfollowUser = async (user) => {
  try {
    await axios.post('/api/unfollow', { user_id: user.id })
    user.is_following = false
    user.follower_count = Math.max(0, (user.follower_count || 1) - 1)
    showToastMessage('已取消关注')
  } catch (error) {
    showToastMessage(error.response?.data?.message || '取消关注失败')
  }
}

const showFollowingList = async () => {
  if (!profileUser.value) return
  try {
    const response = await axios.get(`/api/users/${profileUser.value.id}/following`)
    followingList.value = response.data.users || []
    switchPage('following')
  } catch (error) {
    showToastMessage('加载失败')
  }
}

const showFollowersList = async () => {
  if (!profileUser.value) return
  try {
    const response = await axios.get(`/api/users/${profileUser.value.id}/followers`)
    followersList.value = response.data.users || []
    switchPage('followers')
  } catch (error) {
    showToastMessage('加载失败')
  }
}

const showMyFollowingList = async () => {
  if (!currentUser.value) return
  try {
    const response = await axios.get(`/api/users/${currentUser.value.id}/following`)
    followingList.value = response.data.users || []
    switchPage('following')
  } catch (error) {
    showToastMessage('加载失败')
  }
}

const showMyFollowersList = async () => {
  if (!currentUser.value) return
  try {
    const response = await axios.get(`/api/users/${currentUser.value.id}/followers`)
    followersList.value = response.data.users || []
    switchPage('followers')
  } catch (error) {
    showToastMessage('加载失败')
  }
}

const toggleLike = async (post) => {
  try {
    if (post.is_liked) {
      await axios.post('/api/unlike', { post_id: post.id })
      post.is_liked = false
      post.likes_count = Math.max(0, (post.likes_count || 1) - 1)
    } else {
      await axios.post('/api/like', { post_id: post.id })
      post.is_liked = true
      post.likes_count = (post.likes_count || 0) + 1
    }
  } catch (error) {
    showToastMessage('操作失败')
  }
}

const viewPostDetail = (post) => {
  showToastMessage('详情页开发中')
}

const updateCharCount = () => {
  charCount.value = postContent.value.length
}

const submitPost = async () => {
  if (!postContent.value.trim()) {
    showToastMessage('请输入内容')
    return
  }

  try {
    await axios.post('/api/posts', { content: postContent.value })
    showToastMessage('发布成功')
    showPostModal.value = false
    postContent.value = ''
    charCount.value = 0

    if (currentPage.value === 'feed') {
      feedPage.value = 1
      loadFeed()
    } else if (currentPage.value === 'me') {
      loadMyProfile()
    }
  } catch (error) {
    showToastMessage(error.response?.data?.message || '发布失败')
  }
}

const closePostModal = (e) => {
  if (!e || e.target.classList.contains('modal')) {
    showPostModal.value = false
  }
}

const handleAvatarChange = (e) => {
  const file = e.target.files[0]
  if (file) {
    const reader = new FileReader()
    reader.onload = (e) => {
      editForm.value.avatar = e.target.result
    }
    reader.readAsDataURL(file)
  }
}

const saveProfile = async () => {
  try {
    const response = await axios.post('/api/profile', {
      nickname: editForm.value.nickname,
      bio: editForm.value.bio,
      avatar: editForm.value.avatar
    })

    currentUser.value = { ...currentUser.value, ...response.data.user }
    localStorage.setItem('user', JSON.stringify(currentUser.value))

    showToastMessage('保存成功')
    switchPage('me')
  } catch (error) {
    showToastMessage(error.response?.data?.message || '保存失败')
  }
}

const logout = () => {
  localStorage.removeItem('user')
  localStorage.removeItem('token')
  window.location.href = '#/login'
  window.location.reload()
}

// 初始化
onMounted(() => {
  const user = localStorage.getItem('user')
  if (!user) {
    window.location.href = '#/login'
    return
  }

  currentUser.value = JSON.parse(user)
  loadFeed()
})
</script>