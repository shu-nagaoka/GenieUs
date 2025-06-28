"""検索履歴UseCase"""

import logging
from datetime import datetime, timedelta
from typing import Any

from src.domain.entities import SearchHistoryEntry
from src.domain.repositories import SearchHistoryRepository


class SearchHistoryUseCase:
    """検索履歴のビジネスロジック"""

    def __init__(self, search_history_repository: SearchHistoryRepository, logger: logging.Logger) -> None:
        self.search_history_repository = search_history_repository
        self.logger = logger

    async def save_search_history(
        self,
        user_id: str,
        query: str,
        results_count: int,
        search_type: str = "web",
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """検索履歴を保存

        Args:
            user_id: ユーザーID
            query: 検索クエリ
            results_count: 検索結果数
            search_type: 検索タイプ（web, internal等）
            metadata: 追加のメタデータ

        Returns:
            Dict[str, Any]: 保存結果

        """
        try:
            self.logger.info(f"検索履歴保存開始: user_id={user_id}, query='{query[:50]}...', type={search_type}")

            # 検索履歴エンティティの作成
            history_entry = SearchHistoryEntry(
                id=f"{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                user_id=user_id,
                query=query,
                search_type=search_type,
                results_count=results_count,
                timestamp=datetime.now(),
                metadata=metadata or {},
                created_at=datetime.now(),
            )

            # リポジトリに保存
            saved_entry = await self.search_history_repository.save(history_entry)

            result = {
                "success": True,
                "history_id": saved_entry.id,
                "user_id": user_id,
                "query": query,
                "search_type": search_type,
                "results_count": results_count,
                "timestamp": saved_entry.timestamp.isoformat(),
            }

            self.logger.info(f"検索履歴保存完了: history_id={saved_entry.id}")
            return result

        except Exception as e:
            self.logger.error(f"検索履歴保存UseCase実行エラー: {e}")
            return self._create_error_response(str(e))

    async def get_search_history(
        self,
        user_id: str,
        search_type: str | None = None,
        days_back: int = 30,
        limit: int = 100,
    ) -> dict[str, Any]:
        """検索履歴を取得

        Args:
            user_id: ユーザーID
            search_type: フィルターする検索タイプ（オプション）
            days_back: 取得する過去の日数
            limit: 最大取得数

        Returns:
            Dict[str, Any]: 検索履歴一覧

        """
        try:
            self.logger.info(f"検索履歴取得開始: user_id={user_id}, search_type={search_type}, days_back={days_back}")

            # 期間の計算
            start_date = datetime.now() - timedelta(days=days_back)

            # リポジトリから履歴を取得
            history_entries = await self.search_history_repository.find_by_user_id(
                user_id=user_id,
                search_type=search_type,
                start_date=start_date,
                limit=limit,
            )

            # レスポンス形式への変換
            history_data = []
            for entry in history_entries:
                entry_data = {
                    "id": entry.id,
                    "query": entry.query,
                    "search_type": entry.search_type,
                    "results_count": entry.results_count,
                    "timestamp": entry.timestamp.isoformat(),
                    "metadata": entry.metadata,
                    "days_ago": (datetime.now() - entry.timestamp).days,
                }
                history_data.append(entry_data)

            result = {
                "success": True,
                "user_id": user_id,
                "history": history_data,
                "total_count": len(history_data),
                "filter_search_type": search_type,
                "days_back": days_back,
            }

            self.logger.info(f"検索履歴取得完了: {len(history_data)}件")
            return result

        except Exception as e:
            self.logger.error(f"検索履歴取得UseCase実行エラー: {e}")
            return self._create_error_response(str(e))

    async def get_popular_queries(self, days_back: int = 7, limit: int = 20) -> dict[str, Any]:
        """人気の検索クエリを取得

        Args:
            days_back: 分析対象の日数
            limit: 最大取得数

        Returns:
            Dict[str, Any]: 人気クエリ一覧

        """
        try:
            self.logger.info(f"人気クエリ取得開始: days_back={days_back}, limit={limit}")

            # 期間の計算
            start_date = datetime.now() - timedelta(days=days_back)

            # リポジトリから人気クエリを取得
            popular_queries = await self.search_history_repository.get_popular_queries(
                start_date=start_date,
                limit=limit,
            )

            # ビジネスロジック: クエリの分類・分析
            categorized_queries = self._categorize_queries(popular_queries)

            result = {
                "success": True,
                "analysis_period_days": days_back,
                "popular_queries": categorized_queries,
                "query_count": len(categorized_queries),
            }

            self.logger.info(f"人気クエリ取得完了: {len(categorized_queries)}件")
            return result

        except Exception as e:
            self.logger.error(f"人気クエリ取得UseCase実行エラー: {e}")
            return self._create_error_response(str(e))

    async def delete_search_history(self, user_id: str, history_id: str | None = None) -> dict[str, Any]:
        """検索履歴を削除

        Args:
            user_id: ユーザーID
            history_id: 削除する履歴のID（Noneの場合は全履歴削除）

        Returns:
            Dict[str, Any]: 削除結果

        """
        try:
            self.logger.info(f"検索履歴削除開始: user_id={user_id}, history_id={history_id}")

            if history_id:
                # 特定の履歴を削除
                deleted_count = await self.search_history_repository.delete_by_id(history_id, user_id)
                action = "特定履歴削除"
            else:
                # ユーザーの全履歴を削除
                deleted_count = await self.search_history_repository.delete_by_user_id(user_id)
                action = "全履歴削除"

            result = {
                "success": True,
                "user_id": user_id,
                "history_id": history_id,
                "deleted_count": deleted_count,
                "action": action,
            }

            self.logger.info(f"検索履歴削除完了: {action}, deleted_count={deleted_count}")
            return result

        except Exception as e:
            self.logger.error(f"検索履歴削除UseCase実行エラー: {e}")
            return self._create_error_response(str(e))

    def _categorize_queries(self, queries: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """クエリの分類・分析（ビジネスロジック）"""
        categorized = []

        for query_data in queries:
            query = query_data.get("query", "")
            count = query_data.get("count", 0)

            # 子育てカテゴリの分類
            category = self._classify_childcare_query(query)

            categorized_query = {
                **query_data,
                "category": category,
                "popularity_score": self._calculate_popularity_score(count),
                "search_frequency": "高" if count > 10 else "中" if count > 3 else "低",
            }
            categorized.append(categorized_query)

        return categorized

    def _classify_childcare_query(self, query: str) -> str:
        """子育てクエリの分類"""
        query_lower = query.lower()

        # カテゴリキーワードマッピング
        category_keywords = {
            "feeding": ["食事", "離乳食", "ミルク", "授乳", "栄養"],
            "sleep": ["睡眠", "寝る", "夜泣き", "寝かしつけ"],
            "development": ["発達", "成長", "発語", "歩く", "milestone"],
            "health": ["健康", "病気", "熱", "咳", "予防接種"],
            "behavior": ["行動", "しつけ", "イヤイヤ", "癇癪"],
            "play": ["遊び", "おもちゃ", "学習", "教育"],
            "safety": ["安全", "事故", "けが", "予防"],
            "outing": ["お出かけ", "イベント", "公園", "外出"],
        }

        for category, keywords in category_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                return category

        return "general"

    def _calculate_popularity_score(self, count: int) -> float:
        """人気度スコアの計算"""
        # 簡単な対数スケール
        import math

        return min(1.0, math.log(count + 1) / math.log(100))

    def _create_error_response(self, error_message: str) -> dict[str, Any]:
        """エラー時のレスポンス作成"""
        return {
            "success": False,
            "error": error_message,
            "history": [],
            "total_count": 0,
        }
