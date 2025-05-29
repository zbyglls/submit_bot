import asyncio
from dataclasses import dataclass
from typing import List, Optional
from telegram.ext import Application, CallbackQueryHandler
from fastapi import FastAPI
from config import TELEGRAM_BOT_TOKEN
from utils import logger, reset_initialization
from bot.bot_instance import set_application, get_bot
from bot.commands import register_commands
from bot.handlers import register_handlers
from bot.callbacks import handle_callback_query
app = FastAPI()


@dataclass
class BotState:
    application: Optional[Application] = None
    tasks: List[asyncio.Task] = None
    
    def __post_init__(self):
        if self.tasks is None:
            self.tasks = []

bot_state = BotState()

async def create_bot():
    """创建并初始化bot"""
    try:
        # 重置初始化状态
        reset_initialization()
        
        # 创建新的Application实例
        bot_state.application = (
            Application.builder()
            .token(TELEGRAM_BOT_TOKEN)
            .build()
        )

        # 设置全局实例并立即标记为已初始化
        set_application(bot_state.application)

        # 初始化机器人
        await bot_state.application.initialize()

        # 注册所有处理器
        register_commands(bot_state.application)
        bot_state.application.add_handler(CallbackQueryHandler(handle_callback_query))
        register_handlers(bot_state.application)
        logger.info("所有处理器注册完成")
        
        # 启动机器人和轮询
        await bot_state.application.start()
        await bot_state.application.updater.start_polling(drop_pending_updates=True)
        logger.info("机器人初始化完成并开始轮询")

        return bot_state.application

    except Exception as e:
        logger.error(f"创建bot实例时出错: {e}", exc_info=True)
        raise

async def start_bot():
    """启动机器人轮询（如果尚未启动）"""
    try:
        if not bot_state.application or not bot_state.application.running:  # 增加实例存在性检查
            bot_state.application = await create_bot()
            if bot_state.application:
                await bot_state.application.updater.start_polling(drop_pending_updates=True)
                logger.info("机器人开始轮询")
        
        return bot_state.application
            
    except Exception as e:
        logger.error(f"启动机器人轮询时出错: {e}", exc_info=True)
        raise

async def stop_bot():
    """停止机器人"""
    if bot_state.application:
        try:
            await bot_state.application.updater.stop()
            await bot_state.application.stop()
            await bot_state.application.shutdown()
            logger.info("机器人已停止")
        except Exception as e:
            logger.error(f"停止机器人时出错: {e}", exc_info=True)



# 定义导出的函数
__all__ = [
    'create_bot',
    'start_bot',
    'stop_bot',
    'get_bot',
    'set_application',
    'bot_state'
]