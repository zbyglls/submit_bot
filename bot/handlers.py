from bot.forbidden_words import ALL_FORBIDDEN_WORDS
from config import BOOM_CHANNEL_ID, RECORDING_CHANNEL_ID
from utils import logger
from telegram import Update
from telegram.ext import MessageHandler, filters, ContextTypes
from bot.limiter import RateLimiter

# 定义投稿模板必填字段
REPORT_REQUIRED_FIELDS = [
    "老师花名",
    "联系方式", 
    "时间",
    "地址",
    "花费",
    "样貌身材",
    "经历",
    "验证留名"
]

RECOMMEND_REQUIRED_FIELDS = [
    "老师花名",
    "联系方式",
    "价格",
    "地址",
    "评价",
    "服务"
]

def validate_template(text: str) -> tuple[bool, str]:
    """
    验证文本是否符合模板格式
    返回: (是否有效, 错误信息)
    """
    if not text:
        return False, "投稿内容不能为空"
        
    # 选择验证模板
    required_fields = REPORT_REQUIRED_FIELDS if "吃🐔雷报" in text else RECOMMEND_REQUIRED_FIELDS
    
    # 检查每个必填字段
    missing_fields = []
    for field in required_fields:
        if f"{field}：" not in text and f"{field}:" not in text:
            missing_fields.append(field)
            
    if missing_fields:
        return False, f"缺少必填字段: {', '.join(missing_fields)}"
        
    return True, ""

class SubmissionHandler:
    def __init__(self):
        self.rate_limiter = RateLimiter()
    async def handle_submission(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理用户投稿"""
        try:
            message = update.message
            user_id = message.from_user.id
            # 检查发送频率
            can_submit, error_msg = self.rate_limiter.can_submit(user_id)
            if not can_submit:
                await message.reply_text(f"❌ {error_msg}")
                return
                
            # 记录本次发送
            self.rate_limiter.add_message(user_id)
            # 验证模板格式
            is_valid, error_msg = validate_template(message.text)
            if is_valid:
                # 检查违禁词
                if contains_forbidden_words(message.text):
                    logger.warning(f"用户 {user_id} 的投稿包含违禁词")
                    await message.reply_text(
                        "❌ 投稿内容包含违禁词！\n"
                        "请修改后重新提交。\n"
                        "注意: 请勿发布违规内容。"
                    )
                    return
                # 转发消息到指定频道
                if "吃🐔雷报" in message.text:
                    await context.bot.send_message(
                        chat_id=BOOM_CHANNEL_ID,
                        text=message.text,
                        parse_mode='HTML',
                        disable_web_page_preview=False
                    )
                    logger.info(f"已转发来自用户 {user_id} 的投稿")
                    await update.message.reply_text(f"✅ 您的投稿已成功转发到频道 {BOOM_CHANNEL_ID}！")
                else:
                    await context.bot.send_message(
                        chat_id=RECORDING_CHANNEL_ID,
                        text=message.text,
                        parse_mode='HTML',
                        disable_web_page_preview=False
                    )
                    logger.info(f"已转发来自用户 {user_id} 的投稿")
                    await update.message.reply_text(f"✅ 您的投稿已成功转发到频道 {RECORDING_CHANNEL_ID}！")
            else:
                await update.message.reply_text("❌ 投稿失败，模板格式不正确！")
        except Exception as e:
            logger.error(f"转发消息失败: {e}")
            await update.message.reply_text("❌ 投稿失败，请稍后重试！")
        
def contains_forbidden_words(text: str) -> bool:
    """检查文本是否包含违禁词"""
    if not text:
        return False
        
    text = text.lower()  # 转换为小写
    found_words = []
    
    for word in ALL_FORBIDDEN_WORDS:
        if word in text:
            found_words.append(word)
            
    if found_words:
        logger.warning(f"检测到违禁词: {', '.join(found_words)}")
        return True
        
    return False




def register_handlers(app):
    """注册所有非命令处理器"""
    logger.info("开始注册处理器")
    submission_handler = SubmissionHandler()
    message_filter = (
        filters.TEXT 
        & filters.ChatType.PRIVATE
        & ~filters.FORWARDED 
        & ~filters.UpdateType.EDITED_MESSAGE
        & ~filters.COMMAND
    )
    app.add_handler(MessageHandler(message_filter, submission_handler.handle_submission))
    logger.info("处理器注册完成")
