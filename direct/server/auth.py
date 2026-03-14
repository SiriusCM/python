from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Request

# JWT 配置
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7天

# 密码加密
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(user_id: int) -> str:
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"user_id": user_id, "exp": expire}
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_token_from_request(request: Request = None) -> Optional[str]:
    if not request:
        return None
    # 优先从 Cookie 获取 token
    token = request.cookies.get('token')
    if token:
        return token
    # 其次从 Authorization header 获取
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        return auth_header[7:]
    return None


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def get_current_user(token: str = None, db=None):
    if not token:
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        if user_id is None:
            return None
    except jwt.PyJWTError:
        return None
    from models import User
    user = db.query(User).filter(User.id == user_id).first()
    return user


def get_current_user_from_request(request: Request = None, db=None):
    from database import get_db as get_db_func
    if db is None:
        db = next(get_db_func())
    token = get_token_from_request(request)
    return get_current_user(token, db)