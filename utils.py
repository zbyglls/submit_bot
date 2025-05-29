import logging
from typing import Optional

# 修改初始化组件定义
_INITIALIZED_COMPONENTS = {
    'bot': False,
    'handlers': False,
    'commands': False
}

def reset_initialization(component: Optional[str] = None) -> None:
    """重置初始化标记
    
    Args:
        component: 要重置的特定组件，如果为None则重置所有组件
    """
    global _INITIALIZED_COMPONENTS
    if component:
        if component in _INITIALIZED_COMPONENTS:
            _INITIALIZED_COMPONENTS[component] = False
            logger.debug(f"已重置组件 {component} 的初始化状态")
    else:
        _INITIALIZED_COMPONENTS = {k: False for k in _INITIALIZED_COMPONENTS}
        logger.info("已重置所有组件的初始化状态")

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
# 创建一个控制台处理器，将日志输出到控制台
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
# 定义日志格式
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
# 将处理器添加到日志记录器
logger.addHandler(console_handler)

def mark_initialized(component: str, force: bool = False) -> bool:
    """标记组件为已初始化状态
    
    Args:
        component: 要标记的组件名称
        force: 是否强制标记（即使已经初始化）
    """
    global _INITIALIZED_COMPONENTS
    if component not in _INITIALIZED_COMPONENTS:
        logger.warning(f"未知的组件: {component}")
        return False
    
    was_initialized = _INITIALIZED_COMPONENTS[component]
    if not was_initialized or force:
        _INITIALIZED_COMPONENTS[component] = True
        logger.debug(f"组件 {component} 已标记为初始化")
    return was_initialized

