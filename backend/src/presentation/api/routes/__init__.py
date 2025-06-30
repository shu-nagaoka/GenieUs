"""APIルーター統合モジュール（MVP版）
Context7 FastAPIパターン + DEVELOPMENT_GUIDELINES.md準拠
"""

from .auth import router as auth_router
from .schedules import router as schedules_router

__all__ = ["auth_router", "schedules_router"]
