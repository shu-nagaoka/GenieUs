"""検索履歴 API

検索履歴管理エンドポイント

コーディング規約準拠:
- Import文ファイル先頭配置
- 型アノテーション完備
- FastAPI Depends統合パターン
- 段階的エラーハンドリング
"""

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from src.application.usecases.search_history_usecase import SearchHistoryUseCase
from src.presentation.api.dependencies import get_logger, get_search_history_usecase

router = APIRouter(prefix="/api/v1/search-history", tags=["search_history"])


class SearchHistorySaveRequest(BaseModel):
    """検索履歴保存リクエスト"""

    user_id: str
    query: str
    results_count: int
    search_type: str = "web"
    metadata: dict[str, Any] | None = None


class SearchHistoryData(BaseModel):
    """検索履歴データ"""

    id: str
    query: str
    search_type: str
    results_count: int
    timestamp: str
    metadata: dict[str, Any] | None = None
    days_ago: int


class PopularQueryData(BaseModel):
    """人気クエリデータ"""

    query: str
    count: int
    category: str
    popularity_score: float
    search_frequency: str


class SearchHistorySaveResponse(BaseModel):
    """検索履歴保存レスポンス"""

    success: bool
    history_id: str | None = None
    user_id: str | None = None
    query: str | None = None
    search_type: str | None = None
    results_count: int | None = None
    timestamp: str | None = None
    error: str | None = None


class SearchHistoryListResponse(BaseModel):
    """検索履歴一覧レスポンス"""

    success: bool
    user_id: str
    history: list[SearchHistoryData]
    total_count: int
    filter_search_type: str | None = None
    days_back: int
    error: str | None = None


class PopularQueriesResponse(BaseModel):
    """人気クエリレスポンス"""

    success: bool
    analysis_period_days: int
    popular_queries: list[PopularQueryData]
    query_count: int
    error: str | None = None


class SearchHistoryDeleteResponse(BaseModel):
    """検索履歴削除レスポンス"""

    success: bool
    user_id: str
    history_id: str | None = None
    deleted_count: int
    action: str
    error: str | None = None


@router.post("/save", response_model=SearchHistorySaveResponse)
async def save_search_history(
    request: SearchHistorySaveRequest,
    search_history_usecase: SearchHistoryUseCase = Depends(get_search_history_usecase),
    logger: logging.Logger = Depends(get_logger),
):
    """検索履歴を保存

    Args:
        request: 検索履歴保存リクエスト
        search_history_usecase: 検索履歴UseCase（DI注入）
        logger: ロガー（DI注入）

    Returns:
        SearchHistorySaveResponse: 保存結果

    """
    try:
        logger.info(
            f"検索履歴保存API開始: user_id={request.user_id}, query='{request.query[:50]}...', type={request.search_type}",
        )

        if not request.query.strip():
            raise HTTPException(status_code=400, detail="検索クエリが空です。")

        if request.results_count < 0:
            raise HTTPException(status_code=400, detail="検索結果数は0以上である必要があります。")

        # UseCase実行
        result = await search_history_usecase.save_search_history(
            user_id=request.user_id,
            query=request.query,
            results_count=request.results_count,
            search_type=request.search_type,
            metadata=request.metadata,
        )

        logger.info(f"検索履歴保存API完了: user_id={request.user_id}, success={result.get('success', False)}")

        return SearchHistorySaveResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"検索履歴保存API実行エラー: {e}")
        raise HTTPException(status_code=500, detail=f"検索履歴保存中にエラーが発生しました: {e!s}")


@router.get("/history/{user_id}", response_model=SearchHistoryListResponse)
async def get_search_history(
    user_id: str,
    search_type: str | None = Query(None, description="フィルターする検索タイプ"),
    days_back: int = Query(30, description="取得する過去の日数", ge=1, le=365),
    limit: int = Query(100, description="最大取得数", ge=1, le=1000),
    search_history_usecase: SearchHistoryUseCase = Depends(get_search_history_usecase),
    logger: logging.Logger = Depends(get_logger),
):
    """検索履歴を取得

    Args:
        user_id: ユーザーID
        search_type: フィルターする検索タイプ（オプション）
        days_back: 取得する過去の日数
        limit: 最大取得数
        search_history_usecase: 検索履歴UseCase（DI注入）
        logger: ロガー（DI注入）

    Returns:
        SearchHistoryListResponse: 検索履歴一覧

    """
    try:
        logger.info(f"検索履歴取得API開始: user_id={user_id}, search_type={search_type}, days_back={days_back}")

        # UseCase実行
        result = await search_history_usecase.get_search_history(
            user_id=user_id,
            search_type=search_type,
            days_back=days_back,
            limit=limit,
        )

        logger.info(f"検索履歴取得API完了: user_id={user_id}, count={result.get('total_count', 0)}")

        # レスポンスデータの変換
        history = []
        for history_data in result.get("history", []):
            history.append(SearchHistoryData(**history_data))

        return SearchHistoryListResponse(
            success=result.get("success", True),
            user_id=result["user_id"],
            history=history,
            total_count=result["total_count"],
            filter_search_type=result.get("filter_search_type"),
            days_back=result["days_back"],
            error=result.get("error"),
        )

    except Exception as e:
        logger.error(f"検索履歴取得API実行エラー: {e}")
        raise HTTPException(status_code=500, detail=f"検索履歴取得中にエラーが発生しました: {e!s}")


@router.get("/popular-queries", response_model=PopularQueriesResponse)
async def get_popular_queries(
    days_back: int = Query(7, description="分析対象の日数", ge=1, le=365),
    limit: int = Query(20, description="最大取得数", ge=1, le=100),
    search_history_usecase: SearchHistoryUseCase = Depends(get_search_history_usecase),
    logger: logging.Logger = Depends(get_logger),
):
    """人気の検索クエリを取得

    Args:
        days_back: 分析対象の日数
        limit: 最大取得数
        search_history_usecase: 検索履歴UseCase（DI注入）
        logger: ロガー（DI注入）

    Returns:
        PopularQueriesResponse: 人気クエリ一覧

    """
    try:
        logger.info(f"人気クエリ取得API開始: days_back={days_back}, limit={limit}")

        # UseCase実行
        result = await search_history_usecase.get_popular_queries(
            days_back=days_back,
            limit=limit,
        )

        logger.info(f"人気クエリ取得API完了: query_count={result.get('query_count', 0)}")

        # レスポンスデータの変換
        popular_queries = []
        for query_data in result.get("popular_queries", []):
            popular_queries.append(PopularQueryData(**query_data))

        return PopularQueriesResponse(
            success=result.get("success", True),
            analysis_period_days=result["analysis_period_days"],
            popular_queries=popular_queries,
            query_count=result["query_count"],
            error=result.get("error"),
        )

    except Exception as e:
        logger.error(f"人気クエリ取得API実行エラー: {e}")
        raise HTTPException(status_code=500, detail=f"人気クエリ取得中にエラーが発生しました: {e!s}")


@router.delete("/history/{user_id}", response_model=SearchHistoryDeleteResponse)
async def delete_search_history(
    user_id: str,
    history_id: str | None = Query(None, description="削除する履歴のID（省略時は全履歴削除）"),
    search_history_usecase: SearchHistoryUseCase = Depends(get_search_history_usecase),
    logger: logging.Logger = Depends(get_logger),
):
    """検索履歴を削除

    Args:
        user_id: ユーザーID
        history_id: 削除する履歴のID（Noneの場合は全履歴削除）
        search_history_usecase: 検索履歴UseCase（DI注入）
        logger: ロガー（DI注入）

    Returns:
        SearchHistoryDeleteResponse: 削除結果

    """
    try:
        logger.info(f"検索履歴削除API開始: user_id={user_id}, history_id={history_id}")

        # UseCase実行
        result = await search_history_usecase.delete_search_history(
            user_id=user_id,
            history_id=history_id,
        )

        logger.info(f"検索履歴削除API完了: user_id={user_id}, deleted_count={result.get('deleted_count', 0)}")

        return SearchHistoryDeleteResponse(**result)

    except Exception as e:
        logger.error(f"検索履歴削除API実行エラー: {e}")
        raise HTTPException(status_code=500, detail=f"検索履歴削除中にエラーが発生しました: {e!s}")


@router.get("/health")
async def health_check(
    logger: logging.Logger = Depends(get_logger),
):
    """検索履歴サービスのヘルスチェック"""
    logger.info("検索履歴API ヘルスチェック")
    return {
        "service": "search_history",
        "status": "healthy",
        "features": {
            "history_save": "available",
            "history_retrieval": "available",
            "popular_queries": "available",
            "history_deletion": "available",
        },
        "supported_search_types": ["web", "internal", "agent", "tool"],
        "endpoints": [
            "/api/v1/search-history/save",
            "/api/v1/search-history/history/{user_id}",
            "/api/v1/search-history/popular-queries",
            "/api/v1/search-history/history/{user_id} [DELETE]",
            "/api/v1/search-history/health",
        ],
    }
