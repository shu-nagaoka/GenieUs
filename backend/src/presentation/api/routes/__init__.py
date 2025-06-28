"""APIルーター統合モジュール（MVP版）
Context7 FastAPIパターン + DEVELOPMENT_GUIDELINES.md準拠
"""

from .schedules import router as schedules_router

__all__ = ["schedules_router"]
