# http_api.py
from fastapi import FastAPI

from ws.io.connection_manager import ConnectionManager
from data.player_model import PlayerData


def create_http_app(manager: ConnectionManager) -> FastAPI:
    """创建HTTP应用实例：注入连接管理器，定义接口逻辑"""
    app_http = FastAPI(title="Game HTTP Service", description="玩家状态查询接口")

    @app_http.get("/health", summary="服务健康检查")
    async def health_check():
        """返回服务状态与当前在线人数"""
        return {
            "status": "healthy",
            "online_players": manager.get_online_count(),
            "service": "HTTP Service",
            "timestamp": manager.get_player_data(None).last_active if manager.get_online_count() > 0 else None
        }

    @app_http.get("/players", response_model=list[PlayerData], summary="获取所有在线玩家")
    async def get_all_players():
        """返回所有在线玩家的基础信息"""
        # 直接返回活跃连接中的所有玩家数据
        return list(manager.active_connections.values())

    return app_http
