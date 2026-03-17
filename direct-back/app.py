import os

from fastapi import FastAPI, Depends, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from auth import create_access_token, get_token_from_request, get_current_user, get_current_user_from_request, \
    get_password_hash, verify_password
from database import get_db
from models import User, Post, Follow, Like
from schemas import RegisterRequest, LoginRequest, ProfileUpdate, PostCreate

# 上传目录
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# FastAPI应用
app = FastAPI(title="Twitter Clone API")

# 配置跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://siriuscm.github.io",
        "https://gcsng.jr.jd.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册
@app.post("/api/register")
def register(data: RegisterRequest, db=Depends(get_db)):
    if db.query(User).filter(User.username == data.username).first():
        return {"success": False, "message": "用户名已存在"}
    if db.query(User).filter(User.email == data.email).first():
        return {"success": False, "message": "邮箱已被注册"}

    user = User(
        username=data.username,
        email=data.email,
        password=get_password_hash(data.password),
        nickname=data.nickname or data.username
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return {"success": True, "message": "注册成功", "user": user.to_dict()}

# 登录
@app.post("/api/login", response_model=dict)
def login(data: LoginRequest, response: Response, db=Depends(get_db)):
    user = db.query(User).filter(
        (User.username == data.username) | (User.email == data.username)
    ).first()

    if not user or not verify_password(data.password, user.password):
        return {"success": False, "message": "用户名或密码错误"}

    token = create_access_token(user.id)

    # 写入 Cookie
    response.set_cookie(
        key="token",
        value=token,
        httponly=True,
        max_age=60 * 60 * 24 * 7,  # 7天
        samesite="lax"
    )

    return {"success": True, "message": "登录成功", "user": user.to_dict()}

# 登出
@app.post("/api/logout", response_model=dict)
def logout(response: Response):
    response.delete_cookie(key="token")
    return {"success": True, "message": "已退出登录"}

# 当前用户
@app.post("/api/me")
def get_me(current_user: User = Depends(get_current_user_from_request)):
    if not current_user:
        return {"success": False, "message": "未登录"}

    return {"success": True, "user": current_user.to_dict()}

# 修改资料
@app.post("/api/profile")
def update_profile(data: ProfileUpdate, current_user: User = Depends(get_current_user_from_request), db=Depends(get_db)):
    if not current_user:
        return {"success": False, "message": "未登录"}

    if data.nickname is not None:
        current_user.nickname = data.nickname
    if data.bio is not None:
        current_user.bio = data.bio
    if data.avatar is not None:
        current_user.avatar = data.avatar

    db.commit()

    return {"success": True, "message": "更新成功", "user": current_user.to_dict()}

# 获取用户信息
@app.post("/api/users/{user_id}")
def get_user(user_id: int, db=Depends(get_db), request: Request = None):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {"success": False, "message": "用户不存在"}

    token = get_token_from_request(request)
    current_user = get_current_user(token, db)
    is_following = False
    if current_user:
        is_following = db.query(Follow).filter_by(
            follower_id=current_user.id,
            following_id=user_id
        ).first() is not None

    return {
        "success": True,
        "user": user.to_dict(),
        "follower_count": db.query(Follow).filter(Follow.following_id == user_id).count(),
        "following_count": db.query(Follow).filter(Follow.follower_id == user_id).count(),
        "post_count": db.query(Post).filter(Post.user_id == user_id).count(),
        "is_following": is_following
    }

# 获取用户帖子
@app.post("/api/users/{user_id}/posts")
def get_user_posts(user_id: int, db=Depends(get_db), request: Request = None):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {"success": False, "message": "用户不存在"}

    posts = db.query(Post).filter(Post.user_id == user_id).order_by(Post.created_at.desc()).all()

    # 获取当前用户点赞的帖子
    liked_post_ids = set()
    token = get_token_from_request(request)
    current_user = get_current_user(token, db)
    if current_user:
        liked_post_ids = {like.post_id for like in db.query(Like).filter(Like.user_id == current_user.id).all()}

    return {"success": True, "posts": [post.to_dict(is_liked=post.id in liked_post_ids) for post in posts]}

# 推荐首页
@app.post("/api/feed")
def get_feed(db=Depends(get_db), request: Request = None):
    token = get_token_from_request(request)
    current_user = get_current_user(token, db)
    user_id = current_user.id if current_user else None

    if user_id:
        following_ids = [f.following_id for f in db.query(Follow).filter(Follow.follower_id == user_id).all()]
        following_ids.append(user_id)
        posts = db.query(Post).filter(Post.user_id.in_(following_ids)).order_by(Post.created_at.desc()).limit(20).all()
    else:
        posts = db.query(Post).order_by(Post.created_at.desc()).limit(20).all()

    # 获取当前用户点赞的帖子
    liked_post_ids = set()
    if current_user:
        liked_post_ids = {like.post_id for like in db.query(Like).filter(Like.user_id == current_user.id).all()}

    return {"success": True, "posts": [post.to_dict(is_liked=post.id in liked_post_ids) for post in posts]}

# 发帖
@app.post("/api/posts")
def create_post(data: PostCreate, current_user: User = Depends(get_current_user_from_request), db=Depends(get_db)):
    if not current_user:
        return {"success": False, "message": "请先登录"}

    content = data.content.strip() if data.content else ""
    if not content:
        return {"success": False, "message": "内容不能为空"}

    if len(content) > 500:
        return {"success": False, "message": "内容不能超过500字"}

    post = Post(user_id=current_user.id, content=content)
    db.add(post)
    db.commit()
    db.refresh(post)

    return {"success": True, "message": "发布成功", "post": post.to_dict()}

# 删除帖子
@app.post("/api/posts/{post_id}/delete")
def delete_post(post_id: int, current_user: User = Depends(get_current_user_from_request), db=Depends(get_db)):
    if not current_user:
        return {"success": False, "message": "请先登录"}

    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        return {"success": False, "message": "帖子不存在"}

    if post.user_id != current_user.id:
        return {"success": False, "message": "无权删除"}

    db.delete(post)
    db.commit()

    return {"success": True, "message": "删除成功"}

# 关注
@app.post("/api/follow/{user_id}")
def follow_user(user_id: int, current_user: User = Depends(get_current_user_from_request), db=Depends(get_db)):
    if not current_user:
        return {"success": False, "message": "请先登录"}

    if current_user.id == user_id:
        return {"success": False, "message": "不能关注自己"}

    if not db.query(User).filter(User.id == user_id).first():
        return {"success": False, "message": "用户不存在"}

    existing = db.query(Follow).filter_by(
        follower_id=current_user.id,
        following_id=user_id
    ).first()

    if existing:
        return {"success": False, "message": "已经关注了"}

    follow = Follow(follower_id=current_user.id, following_id=user_id)
    db.add(follow)
    db.commit()

    return {"success": True, "message": "关注成功"}

# 取消关注
@app.post("/api/follow/{user_id}/unfollow")
def unfollow_user(user_id: int, current_user: User = Depends(get_current_user_from_request), db=Depends(get_db)):
    if not current_user:
        return {"success": False, "message": "请先登录"}

    follow = db.query(Follow).filter_by(
        follower_id=current_user.id,
        following_id=user_id
    ).first()

    if not follow:
        return {"success": False, "message": "尚未关注"}

    db.delete(follow)
    db.commit()

    return {"success": True, "message": "取消关注成功"}

# 关注列表
@app.post("/api/users/{user_id}/following")
def get_following(user_id: int, db=Depends(get_db)):
    if not db.query(User).filter(User.id == user_id).first():
        return {"success": False, "message": "用户不存在"}

    following = db.query(Follow).filter(Follow.follower_id == user_id).all()

    return {"success": True, "users": [f.following.to_dict() for f in following]}

# 粉丝列表
@app.post("/api/users/{user_id}/followers")
def get_followers(user_id: int, db=Depends(get_db)):
    if not db.query(User).filter(User.id == user_id).first():
        return {"success": False, "message": "用户不存在"}

    followers = db.query(Follow).filter(Follow.following_id == user_id).all()

    return {"success": True, "users": [f.follower.to_dict() for f in followers]}

# 点赞
@app.post("/api/posts/{post_id}/like")
def like_post(post_id: int, current_user: User = Depends(get_current_user_from_request), db=Depends(get_db)):
    if not current_user:
        return {"success": False, "message": "请先登录"}

    if not db.query(Post).filter(Post.id == post_id).first():
        return {"success": False, "message": "帖子不存在"}

    existing = db.query(Like).filter_by(user_id=current_user.id, post_id=post_id).first()
    if existing:
        return {"success": False, "message": "已经点赞过了"}

    like = Like(user_id=current_user.id, post_id=post_id)
    db.add(like)
    db.commit()

    return {"success": True, "message": "点赞成功"}

# 搜索
@app.post("/api/search")
def search_users(keyword: str = "", db=Depends(get_db)):
    if not keyword:
        return {"success": True, "users": []}

    users = db.query(User).filter(
        (User.username.like(f"%{keyword}%")) |
        (User.nickname.like(f"%{keyword}%"))
    ).limit(20).all()

    return {"success": True, "users": [user.to_dict() for user in users]}

# 推荐
@app.post("/api/suggestions")
def get_suggestions(db=Depends(get_db), request: Request = None):
    token = get_token_from_request(request)
    current_user = get_current_user(token, db)

    query = db.query(User)
    if current_user:
        following_ids = [f.following_id for f in db.query(Follow).filter(Follow.follower_id == current_user.id).all()]
        following_ids.append(current_user.id)
        query = query.filter(~User.id.in_(following_ids))

    users = query.order_by(User.created_at.desc()).limit(10).all()

    return {"success": True, "users": [user.to_dict() for user in users]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)