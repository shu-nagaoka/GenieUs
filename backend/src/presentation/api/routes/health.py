"""ヘルスチェックAPIエンドポイント
Context7 FastAPIパターン準拠
"""

from fastapi import APIRouter

from src.share.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter()


@router.get("/health")
async def health_check() -> dict[str, str]:
    """ヘルスチェックエンドポイント"""
    logger.info("Health check requested")
    return {"status": "healthy", "service": "GieieNest API", "version": "1.0.0"}
