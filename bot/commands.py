from utils import logger
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CommandHandler, ContextTypes


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /start 命令"""
    try:    
        # 默认欢迎消息
        welcome_message = (
            f"👋 你好 {update.message.from_user.first_name}!\n\n"
            "欢迎使用投稿机器人！你可以：\n"
            "1. 投稿雷报💩\n"
            "2. 推荐老师❤\n\n"
            "选择下方按钮获取对应模板"
        )
        
        keyboard = [
            [InlineKeyboardButton("雷报💩", callback_data='boom_report')],
            [InlineKeyboardButton("推荐❤", callback_data='recommend')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
            
        await update.message.reply_text(welcome_message, reply_markup=reply_markup)
    except Exception as e:
        logger.error(f"处理 /start 命令时出错: {e}", exc_info=True)
        await update.message.reply_text("❌ 处理请求时出错，请稍后重试")

def register_commands(app):
    """注册所有命令处理器"""
    app.add_handler(CommandHandler("start", start_command))

