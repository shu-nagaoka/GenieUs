from typing import Protocol, List, Any


class WebSearcherProtocol(Protocol):
    """Web検索機能のインターフェース"""

    async def search_web(self, query: str, num_results: int = 10, search_type: str = "general") -> List[dict[str, Any]]:
        """Web検索を実行

        Args:
            query: 検索クエリ
            num_results: 取得する結果数
            search_type: 検索タイプ

        Returns:
            List[dict[str, Any]]: 検索結果のリスト

        """
        ...
