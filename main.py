import asyncio
from contextlib import asynccontextmanager
from datetime import datetime, timezone
import json
from fastapi import FastAPI, Request
from bot import create_bot, stop_bot, bot_state
from utils import logger
from fastapi import FastAPI, Response


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    try:
        # 初始化机器人
        await create_bot()
        
        logger.info("应用初始化完成")
        yield
        
        # 关闭时清理
        logger.info("开始清理资源...")
        for task in bot_state.tasks:
            if not task.done():
                task.cancel()
        
        if bot_state.tasks:
            await asyncio.gather(*bot_state.tasks, return_exceptions=True)

        await stop_bot()
        logger.info("资源清理完成")
    except Exception as e:
        logger.error(f"生命周期管理出错: {e}", exc_info=True)
        raise



# 创建FastAPI应用
app = FastAPI(lifespan=lifespan)

@app.head("/health")
@app.get("/health")
async def health_check(request: Request):
    """健康检查接口"""
    try:
        if request.method == "HEAD":
            return Response(status_code=200)
        
        status = {
            "bot": False,
            "details": [],
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        # 检查 bot 状态
        try:
            if bot_state.application and bot_state.application.bot:
                me = await bot_state.application.bot.get_me()
                if me and me.id:
                    status["bot"] = True
                    status["details"].append(f"Bot 正常运行 (ID: {me.id})")
            else:
                status["details"].append("Bot 未初始化或未连接")
                logger.warning("健康检查 - Bot 未初始化")
        except Exception as e:
            status["details"].append(f"Bot 状态检查失败: {str(e)}")
            logger.error(f"健康检查 - Bot 状态检查失败: {e}")

        # 确定响应状态码和消息
        is_healthy = all([status["bot"]])
        response_data = {
            "status": "healthy" if is_healthy else "unhealthy",
            "checks": status
        }

        return Response(
            content=json.dumps(response_data, ensure_ascii=False),
            status_code=200 if is_healthy else 503,
            media_type="application/json"
        )

    except Exception as e:
        error_response = {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        logger.error(f"健康检查执行失败: {e}", exc_info=True)
        return Response(
            content=json.dumps(error_response, ensure_ascii=False),
            status_code=503,
            media_type="application/json"
        )
    
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)