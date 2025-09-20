import asyncio
from datetime import datetime

from fastapi import WebSocket

from ws.data.player_model import PlayerData
from ws.io.message_handler import message_handler
from ws.msg import msg_pb2 as msg


# --------------------------
# ChatMessage消息的具体业务逻辑
# --------------------------
@message_handler.on_chat_message
async def handle_chat_message(
        websocket: WebSocket,
        player_data: PlayerData,
        received_msg: msg.Message,
) -> None:
    """处理聊天消息：记录发送者、验证内容、广播给所有玩家"""
    manager = message_handler.manager

    # 提取ChatMessage内容
    chat_msg = received_msg.chatMessage

    # 更新玩家活跃时间
    player_data.last_active = asyncio.get_event_loop().time()

    # 消息内容验证
    if not chat_msg.content.strip():
        print(f"⚠️ [玩家{chat_msg.senderId}] 发送了空消息")
        return

    if len(chat_msg.content) > 500:
        print(f"⚠️ [玩家{chat_msg.senderId}] 消息过长（{len(chat_msg.content)}字符）")
        return

    # 打印格式化日志
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"💬 [{timestamp}] [玩家{chat_msg.senderId}] 发送消息: {chat_msg.content}")

    # 广播聊天消息
    try:
        binary_message = received_msg.SerializeToString()
        await manager.broadcast(binary_message)
    except Exception as e:
        print(f"广播聊天消息失败: {str(e)}")
