# boot.py（程序入口：整合所有模块，启动双端口服务）
import asyncio
import sys
from pathlib import Path

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

# 将项目目录添加到Python路径（确保导入的是当前目录的模块，避免冲突）
sys.path.append(str(Path(__file__).parent))

# 导入核心模块
from ws.io.connection_manager import ConnectionManager
from ws.io.message_handler import message_handler
from ws.module.move import handle_move_message
from http_api import create_http_app
from msg import msg_pb2 as msg

# --------------------------
# 初始化核心组件（确保依赖正确）
# --------------------------
# 1. 创建真实的连接管理器（用于实际运行，替换message_handler中的临时实例）
real_connection_manager = ConnectionManager()

# 2. 更新消息处理器的连接管理器为真实实例（关键：确保广播等操作生效）
message_handler.manager = real_connection_manager
# 重新注册处理函数（确保处理函数绑定真实的连接管理器）
message_handler.on_move_message(handle_move_message)

# 3. 创建WebSocket服务实例（40001端口）
app_websocket = FastAPI(title="Game WebSocket Service", description="Protobuf协议的玩家通信服务")

# 4. 创建HTTP服务实例（40002端口，注入真实连接管理器）
app_http = create_http_app(real_connection_manager)


# --------------------------
# WebSocket主端点（/game路径）
# --------------------------
@app_websocket.websocket("/game")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket连接端点：处理连接建立、消息接收与路由"""
    # 1. 建立连接，获取玩家数据
    player_data = await real_connection_manager.connect(websocket)

    try:
        # 2. 循环接收客户端消息（持续监听）
        while True:
            # 接收二进制消息（Protobuf格式）
            binary_data = await websocket.receive_bytes()
            # 解析Protobuf消息
            received_msg = msg.Message()
            received_msg.ParseFromString(binary_data)
            # 路由消息到对应处理器（调用message_handler）
            await message_handler.route_message(websocket, player_data, received_msg)

    except WebSocketDisconnect:
        # 3. 客户端主动断开连接
        real_connection_manager.disconnect(websocket)
    except Exception as e:
        # 4. 处理其他异常（如消息解析失败、网络错误等）
        print(f"❌ WebSocket错误: {str(e)}")
        real_connection_manager.disconnect(websocket)


# --------------------------
# 启动双端口服务（WebSocket:40001，HTTP:40002）
# --------------------------
async def run_dual_servers():
    """同时启动WebSocket和HTTP服务"""
    # 配置WebSocket服务（40001端口，允许外部设备访问）
    config_ws = uvicorn.Config(
        app_websocket,
        host="0.0.0.0",  # 0.0.0.0表示允许局域网内其他设备连接
        port=40001,
        log_level="info",
        reload=False  # 生产环境关闭reload，开发环境可设为True
    )

    # 配置HTTP服务（40002端口）
    config_http = uvicorn.Config(
        app_http,
        host="0.0.0.0",
        port=40002,
        log_level="info",
        reload=False
    )

    # 同时启动两个服务
    server_ws = uvicorn.Server(config_ws)
    server_http = uvicorn.Server(config_http)
    await asyncio.gather(server_ws.serve(), server_http.serve())


# --------------------------
# 启动程序
# --------------------------
if __name__ == "__main__":
    print("🚀 游戏服务器启动中...")
    print("📡 WebSocket服务：ws://0.0.0.0:40001/game")
    print("🌐 HTTP服务：http://0.0.0.0:40002/docs")
    asyncio.run(run_dual_servers())
