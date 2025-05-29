import os
from pathlib import Path
from dotenv import load_dotenv

# 获取项目根目录
BASE_DIR = Path(__file__).resolve().parent


# 加载环境变量
env_path = BASE_DIR / '.env'
load_dotenv(env_path)

# Telegram 配置
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
BOOM_CHANNEL_ID = os.getenv('BOOM_CHANNEL_ID')
RECORDING_CHANNEL_ID = os.getenv('RECORDING_CHANNEL_ID')

# 速率限制配置
RATE_LIMIT = {
    'MAX_MESSAGES': 10,      # 每个时间窗口允许的最大消息数
    'TIME_WINDOW': 600,     # 时间窗口大小(秒)
    'COOLDOWN_TIME': 900,  # 超限后的冷却时间(秒)
}