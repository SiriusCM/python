// 全局状态
let currentUser = null;
let currentPage = 1;
let viewingUserId = null;
let isFollowing = false;

// 初始化
async function init() {
    await checkLogin();
    setupEventListeners();
}

// 检查登录状态
async function checkLogin() {
    try {
        const res = await fetch('/api/me', {
            method: 'POST',
            credentials: 'include'
        });
        const data = await res.json();
        if (data.success) {
            currentUser = data.user;
            showMainApp();
        }
    } catch (e) {
        window.location.href = '/login';
    }
}

// 显示主应用
function showMainApp() {
    document.getElementById('header').style.display = 'flex';
    document.getElementById('tabbar').style.display = 'flex';
    document.getElementById('fab').style.display = 'flex';
    showPage('feedPage');
    loadFeed();
    loadMyProfile();
    loadSuggestions();
}

// 设置事件监听
function setupEventListeners() {
    document.getElementById('postContent').addEventListener('input', function() {
        const count = this.value.length;
        document.getElementById('charCount').textContent = count;
        document.querySelector('.post-char-count').classList.toggle('warning', count > 450);
    });

    document.getElementById('backBtn').addEventListener('click', goBack);
}

// 显示页面
function showPage(pageId) {
    document.querySelectorAll('.page').forEach(page => {
        page.classList.remove('active');
    });

    document.getElementById(pageId).classList.add('active');

    document.querySelectorAll('.tabbar-item').forEach(item => {
        item.classList.remove('active');
        if (item.dataset.page === pageId) {
            item.classList.add('active');
        }
    });

    updateHeader(pageId);

    if (pageId === 'feedPage') {
        loadFeed();
    } else if (pageId === 'searchPage') {
        loadSuggestions();
    } else if (pageId === 'mePage') {
        loadMyProfile();
    }
}

// 更新头部
function updateHeader(pageId) {
    const backBtn = document.getElementById('backBtn');
    const title = document.getElementById('headerTitle');

    const mainPages = ['feedPage', 'searchPage', 'mePage'];

    if (mainPages.includes(pageId)) {
        backBtn.style.display = 'none';

        if (pageId === 'feedPage') title.textContent = '首页';
        else if (pageId === 'searchPage') title.textContent = '发现';
        else if (pageId === 'mePage') title.textContent = '我的';
    } else {
        backBtn.style.display = 'block';

        if (pageId === 'profilePage') title.textContent = '个人资料';
        else if (pageId === 'editProfilePage') title.textContent = '编辑资料';
        else if (pageId === 'followingPage') title.textContent = '关注';
        else if (pageId === 'followersPage') title.textContent = '粉丝';
    }
}

// 返回
function goBack() {
    const activePage = document.querySelector('.page.active').id;

    if (activePage === 'profilePage' || activePage === 'followingPage' || activePage === 'followersPage') {
        if (viewingUserId === currentUser.id) {
            showPage('mePage');
        } else {
            showPage('feedPage');
        }
    } else if (activePage === 'editProfilePage') {
        showPage('mePage');
    } else {
        showPage('feedPage');
    }
}

// Toast提示
function showToast(message) {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.classList.add('show');
    setTimeout(() => toast.classList.remove('show'), 2500);
}

// 登出
async function logout() {
    try {
        await fetch('/api/logout', { method: 'POST', credentials: 'include' });
        window.location.href = '/login';
    } catch (e) {
        showToast('退出失败');
    }
}

// 加载Feed
async function loadFeed(refresh = true) {
    if (refresh) currentPage = 1;

    try {
        const res = await fetch('/api/feed', {
            method: 'POST',
            credentials: 'include'
        });
        const data = await res.json();

        if (data.success) {
            renderFeed(data.posts, refresh);
            document.getElementById('feedLoadMore').style.display = data.posts.length >= 20 ? 'block' : 'none';
        }
    } catch (e) {
        showToast('加载失败');
    }
}

async function loadMoreFeed() {
    currentPage++;
    await loadFeed(false);
}

// 渲染Feed
function renderFeed(posts, refresh) {
    const container = document.getElementById('feedList');

    if (refresh) {
        container.innerHTML = '';
    }

    if (posts.length === 0 && refresh) {
        container.innerHTML = '<div class="empty-state"><i class="ri-mist-line"></i><p>还没有任何帖子</p></div>';
        return;
    }

    posts.forEach(post => {
        container.innerHTML += renderPostItem(post);
    });
}

// 渲染帖子
function renderPostItem(post) {
    const time = formatTime(post.created_at);
    const avatar = post.author.avatar || '/static/default-avatar.png';

    let imageHtml = '';
    if (post.image) {
        imageHtml = `<div class="post-image"><img src="${post.image}" alt=""></div>`;
    }

    return `
        <div class="post-item" onclick="viewUser(${post.user_id})">
            <div class="post-avatar">
                <img src="${avatar}" alt="头像" onerror="this.src='/static/default-avatar.png'">
            </div>
            <div class="post-content">
                <div class="post-header">
                    <span class="post-nickname">${post.author.nickname}</span>
                    <span class="post-username">@${post.author.username}</span>
                    <span class="post-time">${time}</span>
                </div>
                <div class="post-text" onclick="event.stopPropagation()">${post.content}</div>
                ${imageHtml}
                <div class="post-actions" onclick="event.stopPropagation()">
                    <div class="post-action" onclick="likePost(${post.id})">
                        <i class="ri-heart-line"></i>
                        <span>${post.like_count || 0}</span>
                    </div>
                    <div class="post-action" onclick="deletePost(${post.id})">
                        <i class="ri-delete-bin-line"></i>
                    </div>
                </div>
            </div>
        </div>
    `;
}

// 格式化时间
function formatTime(timeStr) {
    if (!timeStr) return '';
    const date = new Date(timeStr);
    const now = new Date();
    const diff = now - date;

    if (diff < 60000) return '刚刚';
    if (diff < 3600000) return Math.floor(diff / 60000) + '分钟前';
    if (diff < 86400000) return Math.floor(diff / 3600000) + '小时前';
    if (diff < 604800000) return Math.floor(diff / 86400000) + '天前';

    return date.toLocaleDateString();
}

// 查看用户资料
async function viewUser(userId) {
    viewingUserId = userId;

    try {
        const res = await fetch(`/api/users/${userId}`, {
            method: 'POST',
            credentials: 'include'
        });
        const data = await res.json();

        if (data.success) {
            const user = data.user;
            isFollowing = data.is_following;

            document.getElementById('profileAvatar').src = user.avatar || '/static/default-avatar.png';
            document.getElementById('profileName').textContent = user.nickname;
            document.getElementById('profileUsername').textContent = '@' + user.username;
            document.getElementById('profileBio').textContent = user.bio || '暂无简介';
            document.getElementById('profileFollowingCount').textContent = data.following_count;
            document.getElementById('profileFollowerCount').textContent = data.follower_count;
            document.getElementById('profilePostCount').textContent = data.post_count;

            const actionsHtml = document.getElementById('profileActions');
            if (userId === currentUser.id) {
                actionsHtml.innerHTML = `<button class="btn btn-outline" onclick="showPage('editProfilePage'); event.stopPropagation()">编辑资料</button>`;
            } else {
                actionsHtml.innerHTML = isFollowing
                    ? `<button class="btn btn-outline" onclick="unfollowUser(${userId}); event.stopPropagation()">已关注</button>`
                    : `<button class="btn" onclick="followUser(${userId}); event.stopPropagation()">关注</button>`;
            }

            loadUserPosts(userId);
            showPage('profilePage');
        }
    } catch (e) {
        showToast('加载失败');
    }
}

// 加载用户帖子
async function loadUserPosts(userId) {
    try {
        const res = await fetch(`/api/users/${userId}/posts`, {
            method: 'POST',
            credentials: 'include'
        });
        const data = await res.json();

        if (data.success) {
            const container = document.getElementById('profilePosts');
            container.innerHTML = '';

            if (data.posts.length === 0) {
                container.innerHTML = '<div class="empty-state"><i class="ri-mist-line"></i><p>还没有发帖</p></div>';
            } else {
                data.posts.forEach(post => {
                    container.innerHTML += renderPostItem(post);
                });
            }
        }
    } catch (e) {
        console.error(e);
    }
}

// 加载自己的资料
async function loadMyProfile() {
    if (!currentUser) return;

    try {
        const res = await fetch(`/api/users/${currentUser.id}`, {
            method: 'POST',
            credentials: 'include'
        });
        const data = await res.json();

        if (data.success) {
            const user = data.user;

            document.getElementById('myAvatar').src = user.avatar || '/static/default-avatar.png';
            document.getElementById('myName').textContent = user.nickname;
            document.getElementById('myUsername').textContent = '@' + user.username;
            document.getElementById('myBio').textContent = user.bio || '暂无简介';
            document.getElementById('myFollowingCount').textContent = data.following_count;
            document.getElementById('myFollowerCount').textContent = data.follower_count;
            document.getElementById('myPostCount').textContent = data.post_count;

            loadMyPosts();
        }
    } catch (e) {
        console.error(e);
    }
}

// 加载自己的帖子
async function loadMyPosts() {
    if (!currentUser) return;

    try {
        const res = await fetch(`/api/users/${currentUser.id}/posts`, {
            method: 'POST',
            credentials: 'include'
        });
        const data = await res.json();

        if (data.success) {
            const container = document.getElementById('myPosts');
            container.innerHTML = '';

            if (data.posts.length === 0) {
                container.innerHTML = '<div class="empty-state"><i class="ri-mist-line"></i><p>还没有发帖</p></div>';
            } else {
                data.posts.forEach(post => {
                    container.innerHTML += renderPostItem(post);
                });
            }
        }
    } catch (e) {
        console.error(e);
    }
}

// 关注用户
async function followUser(userId) {
    try {
        const res = await fetch(`/api/follow/${userId}`, {
            method: 'POST',
            credentials: 'include'
        });
        const data = await res.json();

        if (data.success) {
            isFollowing = true;
            document.getElementById('profileActions').innerHTML =
                `<button class="btn btn-outline" onclick="unfollowUser(${userId}); event.stopPropagation()">已关注</button>`;
            showToast('关注成功');
            document.getElementById('profileFollowerCount').textContent =
                parseInt(document.getElementById('profileFollowerCount').textContent) + 1;
        } else {
            showToast(data.message);
        }
    } catch (e) {
        showToast('操作失败');
    }
}

// 取消关注
async function unfollowUser(userId) {
    try {
        const res = await fetch(`/api/follow/${userId}/unfollow`, {
            method: 'POST',
            credentials: 'include'
        });
        const data = await res.json();

        if (data.success) {
            isFollowing = false;
            document.getElementById('profileActions').innerHTML =
                `<button class="btn" onclick="followUser(${userId}); event.stopPropagation()">关注</button>`;
            showToast('取消关注');
            document.getElementById('profileFollowerCount').textContent =
                parseInt(document.getElementById('profileFollowerCount').textContent) - 1;
        } else {
            showToast(data.message);
        }
    } catch (e) {
        showToast('操作失败');
    }
}

// 点赞帖子
async function likePost(postId) {
    try {
        const res = await fetch(`/api/posts/${postId}/like`, {
            method: 'POST',
            credentials: 'include'
        });
        const data = await res.json();

        if (data.success) {
            showToast('点赞成功');
            loadFeed();
        } else {
            showToast(data.message);
        }
    } catch (e) {
        showToast('操作失败');
    }
}

// 删除帖子
async function deletePost(postId) {
    if (!confirm('确定删除这条帖子？')) return;

    try {
        const res = await fetch(`/api/posts/${postId}/delete`, {
            method: 'POST',
            credentials: 'include'
        });
        const data = await res.json();

        if (data.success) {
            showToast('删除成功');
            loadFeed();
        } else {
            showToast(data.message);
        }
    } catch (e) {
        showToast('操作失败');
    }
}

// 加载推荐
async function loadSuggestions() {
    try {
        const res = await fetch('/api/suggestions', {
            method: 'POST',
            credentials: 'include'
        });
        const data = await res.json();

        if (data.success) {
            const container = document.getElementById('suggestionsList');
            container.innerHTML = '';

            data.users.forEach(user => {
                container.innerHTML += `
                    <div class="suggestion-item">
                        <img src="${user.avatar || '/static/default-avatar.png'}" alt="" onerror="this.src='/static/default-avatar.png'">
                        <div class="suggestion-item-info">
                            <div class="suggestion-item-name">${user.nickname}</div>
                            <div class="suggestion-item-username">@${user.username}</div>
                        </div>
                        <button class="btn" onclick="followUser(${user.id}); event.stopPropagation()">关注</button>
                    </div>
                `;
            });
        }
    } catch (e) {
        console.error(e);
    }
}

// 搜索用户
async function searchUsers() {
    const keyword = document.getElementById('searchInput').value.trim();

    if (!keyword) {
        document.getElementById('searchResults').innerHTML = '';
        return;
    }

    try {
        const res = await fetch('/api/search', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ keyword })
        });
        const data = await res.json();

        if (data.success) {
            const container = document.getElementById('searchResults');
            container.innerHTML = '';

            data.users.forEach(user => {
                container.innerHTML += `
                    <div class="user-item" onclick="viewUser(${user.id})">
                        <div class="user-item-avatar">
                            <img src="${user.avatar || '/static/default-avatar.png'}" alt="" onerror="this.src='/static/default-avatar.png'">
                        </div>
                        <div class="user-item-info">
                            <div class="user-item-name">${user.nickname}</div>
                            <div class="user-item-username">@${user.username}</div>
                        </div>
                    </div>
                `;
            });
        }
    } catch (e) {
        console.error(e);
    }
}

// 发帖弹窗
function openPostModal() {
    document.getElementById('postModal').classList.add('active');
    document.getElementById('postContent').focus();
}

function closePostModal(event) {
    if (event && event.target !== event.currentTarget) return;
    document.getElementById('postModal').classList.remove('active');
    document.getElementById('postContent').value = '';
    document.getElementById('charCount').textContent = '0';
}

// 发布帖子
async function submitPost() {
    const content = document.getElementById('postContent').value.trim();

    if (!content) {
        showToast('请输入内容');
        return;
    }

    try {
        const res = await fetch('/api/posts', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ content })
        });
        const data = await res.json();

        if (data.success) {
            closePostModal();
            showToast('发布成功');
            loadFeed();
            loadMyProfile();
        } else {
            showToast(data.message);
        }
    } catch (e) {
        showToast('发布失败');
    }
}

// 显示关注列表
async function showFollowing() {
    if (!viewingUserId) return;

    try {
        const res = await fetch(`/api/users/${viewingUserId}/following`, {
            method: 'POST',
            credentials: 'include'
        });
        const data = await res.json();

        if (data.success) {
            renderUserList(data.users, 'followingList');
            showPage('followingPage');
        }
    } catch (e) {
        showToast('加载失败');
    }
}

// 显示粉丝列表
async function showFollowers() {
    if (!viewingUserId) return;

    try {
        const res = await fetch(`/api/users/${viewingUserId}/followers`, {
            method: 'POST',
            credentials: 'include'
        });
        const data = await res.json();

        if (data.success) {
            renderUserList(data.users, 'followersList');
            showPage('followersPage');
        }
    } catch (e) {
        showToast('加载失败');
    }
}

// 显示自己的关注
async function showMyFollowing() {
    viewingUserId = currentUser.id;
    await showFollowing();
}

// 显示自己的粉丝
async function showMyFollowers() {
    viewingUserId = currentUser.id;
    await showFollowers();
}

// 渲染用户列表
function renderUserList(users, containerId) {
    const container = document.getElementById(containerId);

    if (users.length === 0) {
        container.innerHTML = '<div class="empty-state"><i class="ri-user-line"></i><p>暂无数据</p></div>';
        return;
    }

    container.innerHTML = '';
    users.forEach(user => {
        container.innerHTML += `
            <div class="user-item" onclick="viewUser(${user.id})">
                <div class="user-item-avatar">
                    <img src="${user.avatar || '/static/default-avatar.png'}" alt="" onerror="this.src='/static/default-avatar.png'">
                </div>
                <div class="user-item-info">
                    <div class="user-item-name">${user.nickname}</div>
                    <div class="user-item-username">@${user.username}</div>
                </div>
            </div>
        `;
    });
}

// 保存资料
async function saveProfile() {
    const nickname = document.getElementById('editNickname').value.trim();
    const bio = document.getElementById('editBio').value.trim();

    try {
        const res = await fetch('/api/profile', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ nickname, bio })
        });
        const data = await res.json();

        if (data.success) {
            showToast('保存成功');
            showPage('mePage');
            loadMyProfile();
        } else {
            showToast(data.message);
        }
    } catch (e) {
        showToast('保存失败');
    }
}

// 初始化应用
init();