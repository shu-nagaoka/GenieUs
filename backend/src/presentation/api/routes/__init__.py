"""APIルーター統合モジュール（MVP版）
Context7 FastAPIパターン + DEVELOPMENT_GUIDELINES.md準拠
"""

from .health import router as health_router
from .multiagent_chat import router as multiagent_router

__all__ = ["health_router", "multiagent_router"]
