from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, Tuple
from config import RATE_LIMIT

class RateLimiter:
    def __init__(self):
        # 用户消息计数器
        self.message_counts: Dict[int, int] = defaultdict(int)
        # 用户最后发送时间
        self.last_message_time: Dict[int, datetime] = defaultdict(datetime.now)
        # 用户冷却时间
        self.cooldowns: Dict[int, datetime] = defaultdict(datetime.now)
        
        # 配置
        self.MAX_MESSAGES = RATE_LIMIT['MAX_MESSAGES']  # 最大消息数
        self.TIME_WINDOW = RATE_LIMIT['TIME_WINDOW']  # 时间窗口(秒)
        self.COOLDOWN_TIME = RATE_LIMIT['COOLDOWN_TIME']  # 冷却时间(秒)

    def can_submit(self, user_id: int) -> Tuple[bool, str]:
        """检查用户是否可以发送消息"""
        now = datetime.now()
        
        # 检查是否在冷却中
        if user_id in self.cooldowns and now < self.cooldowns[user_id]:
            remaining = (self.cooldowns[user_id] - now).seconds
            return False, f"您需要等待 {remaining} 秒后才能继续投稿"
            
        # 清理过期的消息计数
        if (now - self.last_message_time[user_id]).seconds > self.TIME_WINDOW:
            self.message_counts[user_id] = 0
            
        # 检查消息频率
        if self.message_counts[user_id] >= self.MAX_MESSAGES:
            self.cooldowns[user_id] = now + timedelta(seconds=self.COOLDOWN_TIME)
            return False, f"发送过于频繁，已被限制 {self.COOLDOWN_TIME/60} 分钟"
            
        return True, ""

    def add_message(self, user_id: int):
        """记录用户消息"""
        self.message_counts[user_id] += 1
        self.last_message_time[user_id] = datetime.now()