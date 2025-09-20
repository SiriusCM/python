# connection_manager.py
from typing import Dict, Optional

from fastapi import WebSocket

from ws.data.player_model import PlayerData


class ConnectionManager:
    """WebSocket连接管理器：处理连接建立、断开、广播及玩家数据关联"""

    def __init__(self):
        # 映射关系：WebSocket连接 → 玩家数据
        self.active_connections: Dict[WebSocket, PlayerData] = {}

    async def connect(self, websocket: WebSocket) -> PlayerData:
        """建立新连接：接受连接并创建玩家数据"""
        await websocket.accept()
        player_data = PlayerData()
        self.active_connections[websocket] = player_data
        print(f"✅ 新玩家连接 | 当前在线: {len(self.active_connections)} 人")
        return player_data

    def disconnect(self, websocket: WebSocket) -> None:
        """断开连接：移除连接与玩家数据的映射"""
        if websocket in self.active_connections:
            del self.active_connections[websocket]
            print(f"❌ 玩家断开连接 | 当前在线: {len(self.active_connections)} 人")

    async def broadcast(self, message: bytes, exclude: Optional[WebSocket] = None) -> None:
        """广播二进制消息：向所有玩家发送（可排除指定连接）"""
        for websocket in self.active_connections:
            if websocket != exclude:
                await websocket.send_bytes(message)

    def get_player_data(self, websocket: WebSocket) -> Optional[PlayerData]:
        """通过WebSocket连接获取对应的玩家数据"""
        return self.active_connections.get(websocket)

    def get_online_count(self) -> int:
        """获取当前在线玩家数量"""
        return len(self.active_connections)
