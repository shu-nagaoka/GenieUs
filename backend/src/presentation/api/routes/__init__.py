"""APIルーター統合モジュール（MVP版）
Context7 FastAPIパターン + DEVELOPMENT_GUIDELINES.md準拠
"""

from .multiagent_chat import router as multiagent_router
from .schedules import router as schedules_router

__all__ = ["multiagent_router", "schedules_router"]
