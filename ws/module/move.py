import asyncio

from fastapi import WebSocket

from ws.data.player_model import PlayerData
from ws.io.message_handler import message_handler
from ws.msg import msg_pb2 as msg


# --------------------------
# MoveMessage消息的具体业务逻辑
# --------------------------
@message_handler.on_move_message
async def handle_move_message(
        websocket: WebSocket,
        player_data: PlayerData,
        received_msg: msg.Message,
) -> None:
    """处理玩家移动消息：更新状态、打印日志、广播消息"""
    manager = message_handler.manager

    # 提取MoveMessage内容
    move_msg = received_msg.moveMessage

    # 更新玩家数据
    player_data.player_id = move_msg.playerId
    player_data.last_active = asyncio.get_event_loop().time()

    # 打印格式化日志
    print(f"📌 [玩家{move_msg.playerId}] 移动信息: "
          f"位置({move_msg.posX:.2f}, {move_msg.posY:.2f}, {move_msg.posZ:.2f}) | "
          f"旋转Y轴: {move_msg.rotY:.2f} | "
          f"在线人数: {manager.get_online_count()}")

    # 广播消息给其他玩家
    try:
        binary_message = received_msg.SerializeToString()
        await manager.broadcast(binary_message, exclude=websocket)
    except Exception as e:
        print(f"广播移动消息失败: {str(e)}")
