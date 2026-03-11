// Toast提示
function showToast(message) {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.classList.add('show');
    setTimeout(() => toast.classList.remove('show'), 2500);
}

// 登录
async function login() {
    const username = document.getElementById('loginUsername').value.trim();
    const password = document.getElementById('loginPassword').value;

    if (!username || !password) {
        showToast('请填写完整信息');
        return;
    }

    try {
        const res = await fetch('/api/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ username, password })
        });
        const data = await res.json();

        if (data.success) {
            showToast('登录成功');
            window.location.href = '/';
        } else {
            showToast(data.message);
        }
    } catch (e) {
        showToast('登录失败');
    }
}

// 回车登录
document.addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        login();
    }
}); }
});