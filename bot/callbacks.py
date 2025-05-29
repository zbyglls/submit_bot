from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from utils import logger


async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理按钮回调"""
    query = update.callback_query

    try:
        # 解析回调数据
        callback_data = query.data
        if callback_data == 'boom_report':
            template = """
            *请按照以下模板提交雷报，出击证明请自行发布在评论区，点击下方模板可直接复制* ⬇️：
            `
吃🐔雷报
老师花名：
联系方式：
时间：
地址：
花费：
样貌身材：
槽点：
经历：
验证留名：

出击证明见评论区（聊天记录或付款记录）
            `
*请填写完整后发送给我～*
            """
            await query.message.reply_text(text=template, parse_mode=ParseMode.MARKDOWN)

        elif callback_data == 'recommend':
            template = """
            *请按照以下模板提交，图片请自行发布在评论区，点击下方模板可直接复制* ⬇️：
            `
网友推荐
老师花名：
联系方式：
价格：
地址：
服务：
评价：
            `
*请填写完整后发送给我～*
            """
            await query.message.reply_text(text=template, parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        logger.error(f"处理回调查询时出错: {e}", exc_info=True)
        await query.message.reply_text("❌ 处理请求时出错，请稍后重试")