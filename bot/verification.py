from datetime import datetime, timezone
from telegram.ext import ContextTypes
from utils import logger


async def check_channel_subscription(bot, user_id: int, channel_id: str = '@yangshyyds') -> bool:
    """检查用户是否关注了指定频道"""
    try:
        chat_member = await bot.get_chat_member(chat_id=channel_id, user_id=user_id)
        return chat_member.status not in ['left', 'kicked', 'restricted']
    except Exception as e:
        logger.error(f"检查频道关注状态时出错: {e}", exc_info=True)
        return False
              