from datetime import datetime
from bot.forbidden_words import ALL_FORBIDDEN_WORDS
from config import BOOM_CHANNEL_ID, RECORDING_CHANNEL_ID
from utils import logger
from typing import Dict, List
from telegram import Update, InputMediaPhoto, InputMediaVideo, Message
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
    "验证留名",
    "出击证明见评论区（聊天记录或付款记录）"
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
    """验证文本是否符合模板格式"""
    if not text:
        return False, "投稿内容不能为空"
        
    # 选择验证模板
    required_fields = REPORT_REQUIRED_FIELDS if "吃🐔雷报" in text else RECOMMEND_REQUIRED_FIELDS
    
    # 检查每个必填字段
    missing_fields = []
    for field in required_fields:
        # 支持多种冒号格式
        colon_variants = ['：', ':', '∶', '︰', '﹕']
        field_found = False
        if f"{field}" in text:
            field_found = True
            break
                
        if not field_found:
            missing_fields.append(field)
            
    if missing_fields:
        return False, f"缺少必填字段: {', '.join(missing_fields)}"
        
    # 检查字段值是否为空或仅包含特殊字符
    empty_fields = []
    lines = text.split('\n')
    for line in lines:
        for field in required_fields:
            for colon in colon_variants:
                if line.startswith(f"{field}{colon}"):
                    value = line.split(colon, 1)[1].strip()
                    if not value or value in ['']:
                        empty_fields.append(field)
                        
    if empty_fields:
        return False, f"以下字段内容不能为空: {', '.join(set(empty_fields))}"
        
    return True, ""


class SubmissionHandler:
    def __init__(self):
        self.rate_limiter = RateLimiter()
        self.media_groups: Dict[str, List[Message]] = {}

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
            text = message.caption if message.caption else message.text
            # 处理媒体组消息
            if message.media_group_id:
                # 初始化媒体组
                if message.media_group_id not in self.media_groups:
                    self.media_groups[message.media_group_id] = {
                        'messages': [],
                        'text': text,
                        'timestamp': datetime.now()
                    }
                
                # 添加到媒体组
                self.media_groups[message.media_group_id]['messages'].append(message)
                if len(self.media_groups[message.media_group_id]['messages']) < 10:
                    logger.info(f"等待媒体组 {message.media_group_id} 的其他文件...")
                    return
            
            media = []
            media_messages = []
            if message.media_group_id and message.media_group_id in self.media_groups:
                media_data = self.media_groups[message.media_group_id]
                media_messages = sorted(media_data['messages'], key=lambda x: x.message_id)
                text = media_data['text']
            elif message.photo or message.video:
                media_messages = [message]
            # 验证模板格式
            is_valid, error_msg = validate_template(text)
            if is_valid:
                # 检查违禁词
                if contains_forbidden_words(text):
                    logger.warning(f"用户 {user_id} 的投稿包含违禁词")
                    await message.reply_text(
                        "❌ 投稿内容包含违禁词！\n"
                        "请修改后重新提交。\n"
                        "注意: 请勿发布违规内容。"
                    )
                    return
                
                if media_messages:
                    first_msg = media_messages[0]
                    if first_msg.photo:
                        media.append(
                            InputMediaPhoto(
                                media=first_msg.photo[-1].file_id,
                                caption=text,
                                parse_mode='HTML'
                            )
                        )
                    elif first_msg.video:
                        media.append(
                            InputMediaVideo(
                                media=first_msg.video.file_id,
                                caption=text,
                                parse_mode='HTML'
                            )
                        )
                        
                # 处理剩余媒体文件
                for msg in media_messages[1:]:
                    if msg.photo:
                        media.append(InputMediaPhoto(media=msg.photo[-1].file_id))
                    elif msg.video:
                        media.append(InputMediaVideo(media=msg.video.file_id))
                
                target_channel_id = BOOM_CHANNEL_ID if "吃🐔雷报" in text else RECORDING_CHANNEL_ID

                if media:
                    # 发送媒体组
                    await context.bot.send_media_group(chat_id=target_channel_id, media=media)
                else:
                    await context.bot.send_message(
                        chat_id=target_channel_id,
                        text=text,
                        parse_mode='HTML',
                        disable_web_page_preview=False
                    )
                
                if message.media_group_id:
                    del self.media_groups[message.media_group_id]

                logger.info(f"已转发来自用户 {user_id} 的投稿")
                await update.message.reply_text(f"✅ 您的投稿已成功转发到频道 {target_channel_id}！")
            else:
                await update.message.reply_text(f"❌ 投稿失败，模板格式不正确！\n{error_msg}")
                logger.info(error_msg)
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
        (filters.TEXT | filters.PHOTO | filters.VIDEO) 
        & filters.ChatType.PRIVATE
        & ~filters.FORWARDED 
        & ~filters.UpdateType.EDITED_MESSAGE
        & ~filters.COMMAND
    )
    app.add_handler(MessageHandler(message_filter, submission_handler.handle_submission))
    logger.info("处理器注册完成")
