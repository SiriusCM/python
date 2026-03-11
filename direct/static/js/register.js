// Toast提示
function showToast(message) {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.classList.add('show');
    setTimeout(() => toast.classList.remove('show'), 2500);
}

// 注册
async function register() {
    const username = document.getElementById('regUsername').value.trim();
    const email = document.getElementById('regEmail').value.trim();
    const nickname = document.getElementById('regNickname').value.trim();
    const password = document.getElementById('regPassword').value;

    if (!username || !email || !password) {
        showToast('请填写完整信息');
        return;
    }

    try {
        const res = await fetch('/api/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ username, email, nickname, password })
        });
        const data = await res.json();

        if (data.success) {
            showToast('注册成功');
            window.location.href = '/login';
        } else {
            showToast(data.message);
        }
    } catch (e) {
        showToast('注册失败');
    }
}

// 回车注册
document.addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        register();
    }
});