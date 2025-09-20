from functools import wraps
from typing import Callable, Dict, TypeVar, Any

from fastapi import WebSocket

from ws.io.connection_manager import ConnectionManager
from ws.data.player_model import PlayerData
from ws.msg import msg_pb2 as msg

# 类型变量，用于装饰器类型提示
T = TypeVar('T')


class MessageHandler:
    """消息处理器：注册消息类型、路由消息、执行业务逻辑"""

    def __init__(self, connection_manager: ConnectionManager):
        self.handlers: Dict[str, Callable] = {}  # 消息类型 → 处理函数映射（直接使用消息字段名）
        self.manager = connection_manager  # 注入连接管理器
        # 定义支持的消息类型列表（替代原有的映射表，更简洁）
        self.supported_messages = ["moveMessage", "chatMessage"]

    def register_handler(self, message_field: str) -> Callable[[Callable[..., T]], Callable[..., T]]:
        """通用装饰器：注册指定消息字段的处理函数"""
        # 校验消息类型是否在支持列表中
        if message_field not in self.supported_messages:
            raise ValueError(f"不支持的消息类型: {message_field}，支持的类型: {self.supported_messages}")

        def decorator(func: Callable[..., T]) -> Callable[..., T]:
            @wraps(func)
            async def wrapper(
                    websocket: WebSocket,
                    player_data: PlayerData,
                    received_msg: msg.Message,
            ) -> Any:
                # 前置校验：确保消息包含指定字段且连接活跃
                if websocket.client_state.CONNECTED and received_msg.HasField(message_field):
                    return await func(websocket, player_data, received_msg)
                return None

            # 直接使用消息字段名作为处理器键（移除映射表）
            self.handlers[message_field] = wrapper
            return wrapper

        return decorator

    # 特定消息类型的装饰器
    def on_move_message(self, func: Callable[..., T]) -> Callable[..., T]:
        """注册MoveMessage类型消息的处理函数"""
        return self.register_handler("moveMessage")(func)

    def on_chat_message(self, func: Callable[..., T]) -> Callable[..., T]:
        """注册ChatMessage类型消息的处理函数"""
        return self.register_handler("chatMessage")(func)

    async def route_message(
            self,
            websocket: WebSocket,
            player_data: PlayerData,
            received_msg: msg.Message
    ) -> None:
        """消息路由：根据消息类型自动调用对应的处理函数"""
        # 遍历支持的消息类型，直接匹配字段名（无需通过映射表）
        for message_field in self.supported_messages:
            if received_msg.HasField(message_field) and message_field in self.handlers:
                try:
                    await self.handlers[message_field](websocket, player_data, received_msg)
                except Exception as e:
                    print(f"处理{message_field}消息时出错: {str(e)}")
                return

        # 未找到匹配的处理器
        print(f"未找到处理函数的消息类型: {received_msg}")


# --------------------------
# 初始化消息处理器（用于装饰器注册）
# --------------------------
temp_manager = ConnectionManager()
message_handler = MessageHandler(temp_manager)
