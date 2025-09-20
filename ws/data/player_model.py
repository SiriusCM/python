# data/player_model.py
import asyncio
from typing import Optional  # 用于可选字段

from pydantic import BaseModel  # 导入 Pydantic 基类


class PlayerData(BaseModel):
    """玩家数据模型（改为 Pydantic 模型）"""
    # 定义字段并指定类型，支持可选字段、默认值等
    player_id: Optional[str] = None  # 玩家ID（可选，初始为 None）
    nickname: Optional[str] = None  # 玩家昵称（可选）
    is_connected: bool = False  # 是否在线（默认 False）
    last_active: float = asyncio.get_event_loop().time()  # 最后活跃时间（时间戳，默认 0）
