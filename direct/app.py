from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from passlib.context import CryptContext

from database import get_db
from models import User, Post, Follow, Like
from schemas import RegisterRequest, LoginRequest, ProfileUpdate, PostCreate

# 密码加密
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# FastAPI应用
app = FastAPI(title="Twitter Clone API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# 页面路由
@app.get("/")
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register")
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

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
        password=pwd_context.hash(data.password),
        nickname=data.nickname or data.username
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return {"success": True, "message": "注册成功", "user": user.to_dict()}

# 登录
@app.post("/api/login")
def login(data: LoginRequest, request: Request, db=Depends(get_db)):
    user = db.query(User).filter(
        (User.username == data.username) | (User.email == data.username)
    ).first()

    if not user or not pwd_context.verify(data.password, user.password):
        return {"success": False, "message": "用户名或密码错误"}

    request.session["user_id"] = user.id
    request.session["username"] = user.username

    return {"success": True, "message": "登录成功", "user": user.to_dict()}

# 登出
@app.post("/api/logout")
def logout(request: Request):
    request.session.clear()
    return {"success": True, "message": "已退出登录"}

# 当前用户
@app.post("/api/me")
def get_me(db=Depends(get_db), request: Request = None):
    user_id = request.session.get("user_id") if request else None
    if not user_id:
        return {"success": False, "message": "未登录"}

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {"success": False, "message": "用户不存在"}

    return {"success": True, "user": user.to_dict()}

# 修改资料
@app.post("/api/profile")
def update_profile(data: ProfileUpdate, db=Depends(get_db), request: Request = None):
    user_id = request.session.get("user_id") if request else None
    if not user_id:
        return {"success": False, "message": "未登录"}

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {"success": False, "message": "用户不存在"}

    if data.nickname is not None:
        user.nickname = data.nickname
    if data.bio is not None:
        user.bio = data.bio
    if data.avatar is not None:
        user.avatar = data.avatar

    db.commit()

    return {"success": True, "message": "更新成功", "user": user.to_dict()}

# 获取用户信息
@app.post("/api/users/{user_id}")
def get_user(user_id: int, db=Depends(get_db), request: Request = None):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {"success": False, "message": "用户不存在"}

    current_user_id = request.session.get("user_id") if request else None
    is_following = False
    if current_user_id:
        is_following = db.query(Follow).filter_by(
            follower_id=current_user_id,
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
def get_user_posts(user_id: int, db=Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {"success": False, "message": "用户不存在"}

    posts = db.query(Post).filter(Post.user_id == user_id).order_by(Post.created_at.desc()).all()

    return {"success": True, "posts": [post.to_dict() for post in posts]}

# 推荐首页
@app.post("/api/feed")
def get_feed(db=Depends(get_db), request: Request = None):
    user_id = request.session.get("user_id") if request else None

    if user_id:
        following_ids = [f.following_id for f in db.query(Follow).filter(Follow.follower_id == user_id).all()]
        following_ids.append(user_id)
        posts = db.query(Post).filter(Post.user_id.in_(following_ids)).order_by(Post.created_at.desc()).limit(20).all()
    else:
        posts = db.query(Post).order_by(Post.created_at.desc()).limit(20).all()

    return {"success": True, "posts": [post.to_dict() for post in posts]}

# 发帖
@app.post("/api/posts")
def create_post(data: PostCreate, db=Depends(get_db), request: Request = None):
    user_id = request.session.get("user_id") if request else None
    if not user_id:
        return {"success": False, "message": "请先登录"}

    content = data.content.strip() if data.content else ""
    if not content:
        return {"success": False, "message": "内容不能为空"}

    if len(content) > 500:
        return {"success": False, "message": "内容不能超过500字"}

    post = Post(user_id=user_id, content=content)
    db.add(post)
    db.commit()
    db.refresh(post)

    return {"success": True, "message": "发布成功", "post": post.to_dict()}

# 删除帖子
@app.post("/api/posts/{post_id}/delete")
def delete_post(post_id: int, db=Depends(get_db), request: Request = None):
    user_id = request.session.get("user_id") if request else None
    if not user_id:
        return {"success": False, "message": "请先登录"}

    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        return {"success": False, "message": "帖子不存在"}

    if post.user_id != user_id:
        return {"success": False, "message": "无权删除"}

    db.delete(post)
    db.commit()

    return {"success": True, "message": "删除成功"}

# 关注
@app.post("/api/follow/{user_id}")
def follow_user(user_id: int, db=Depends(get_db), request: Request = None):
    current_user_id = request.session.get("user_id") if request else None
    if not current_user_id:
        return {"success": False, "message": "请先登录"}

    if current_user_id == user_id:
        return {"success": False, "message": "不能关注自己"}

    if not db.query(User).filter(User.id == user_id).first():
        return {"success": False, "message": "用户不存在"}

    existing = db.query(Follow).filter_by(
        follower_id=current_user_id,
        following_id=user_id
    ).first()

    if existing:
        return {"success": False, "message": "已经关注了"}

    follow = Follow(follower_id=current_user_id, following_id=user_id)
    db.add(follow)
    db.commit()

    return {"success": True, "message": "关注成功"}

# 取消关注
@app.post("/api/follow/{user_id}/unfollow")
def unfollow_user(user_id: int, db=Depends(get_db), request: Request = None):
    current_user_id = request.session.get("user_id") if request else None
    if not current_user_id:
        return {"success": False, "message": "请先登录"}

    follow = db.query(Follow).filter_by(
        follower_id=current_user_id,
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
def like_post(post_id: int, db=Depends(get_db), request: Request = None):
    user_id = request.session.get("user_id") if request else None
    if not user_id:
        return {"success": False, "message": "请先登录"}

    if not db.query(Post).filter(Post.id == post_id).first():
        return {"success": False, "message": "帖子不存在"}

    existing = db.query(Like).filter_by(user_id=user_id, post_id=post_id).first()
    if existing:
        return {"success": False, "message": "已经点赞过了"}

    like = Like(user_id=user_id, post_id=post_id)
    db.add(like)
    db.commit()

    return {"success": True, "message": "点赞成功"}

# 取消点赞
@app.post("/api/posts/{post_id}/unlike")
def unlike_post(post_id: int, db=Depends(get_db), request: Request = None):
    user_id = request.session.get("user_id") if request else None
    if not user_id:
        return {"success": False, "message": "请先登录"}

    like = db.query(Like).filter_by(user_id=user_id, post_id=post_id).first()
    if not like:
        return {"success": False, "message": "尚未点赞"}

    db.delete(like)
    db.commit()

    return {"success": True, "message": "取消点赞成功"}

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
    user_id = request.session.get("user_id") if request else None

    query = db.query(User)
    if user_id:
        following_ids = [f.following_id for f in db.query(Follow).filter(Follow.follower_id == user_id).all()]
        following_ids.append(user_id)
        query = query.filter(~User.id.in_(following_ids))

    users = query.order_by(User.created_at.desc()).limit(10).all()

    return {"success": True, "users": [user.to_dict() for user in users]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)