import os
import logging
from typing import List, Any, Optional
import json
import aiohttp
from urllib.parse import quote

from src.application.interface.protocols.web_searcher import WebSearcherProtocol


class GoogleSearchAdapter(WebSearcherProtocol):
    """Google Custom Search APIを使用したWeb検索アダプター"""

    def __init__(self, logger: logging.Logger) -> None:
        self.logger = logger
        self.api_key = os.getenv("GOOGLE_SEARCH_API_KEY")
        self.search_engine_id = os.getenv("GOOGLE_SEARCH_ENGINE_ID")
        self.base_url = "https://www.googleapis.com/customsearch/v1"

    async def search_web(self, query: str, num_results: int = 10, search_type: str = "general") -> List[dict[str, Any]]:
        """Google Custom Search APIでWeb検索を実行"""
        try:
            # API Key チェック
            if not self.api_key or not self.search_engine_id:
                self.logger.warning("Google Search API設定が不完全です - デモモードで動作")
                return self._create_demo_results(query, search_type)

            self.logger.info(f"Google Search API実行: query='{query}', num_results={num_results}")

            # 検索パラメータ構築
            params = {
                "key": self.api_key,
                "cx": self.search_engine_id,
                "q": query,
                "num": min(num_results, 10),  # Google APIは最大10件
                "lr": "lang_ja",  # 日本語の結果を優先
                "gl": "jp",  # 日本の結果を優先
            }

            # 検索タイプに応じた追加パラメータ
            if search_type == "medical":
                params["q"] += " 医療 病院 クリニック"
            elif search_type == "facility":
                params["q"] += " 施設 センター"

            # API呼び出し
            async with aiohttp.ClientSession() as session:
                async with session.get(self.base_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_search_results(data)
                    else:
                        self.logger.error(f"Google Search APIエラー: {response.status}")
                        return self._create_demo_results(query, search_type)

        except Exception as e:
            self.logger.error(f"Web検索エラー: {e}")
            return self._create_demo_results(query, search_type)

    def _parse_search_results(self, data: dict) -> List[dict[str, Any]]:
        """Google Search APIレスポンスをパース"""
        results = []

        items = data.get("items", [])
        for item in items:
            result = {
                "title": item.get("title", ""),
                "link": item.get("link", ""),
                "snippet": item.get("snippet", ""),
                "displayLink": item.get("displayLink", ""),
            }
            results.append(result)

        self.logger.info(f"Google Search API結果パース完了: {len(results)}件")
        return results

    def _create_demo_results(self, query: str, search_type: str) -> List[dict[str, Any]]:
        """デモ用の検索結果を生成"""
        self.logger.info(f"デモモード: query='{query}', search_type='{search_type}'")

        demo_results = []

        if search_type == "medical":
            demo_results = [
                {
                    "title": f"【{query}】に関する小児科・医療機関情報",
                    "link": "https://example.com/medical",
                    "snippet": f"申し訳ございません。現在は検索機能のデモモードです。実際のGoogle Search API設定が完了すると、{query}に関する医療機関の詳細情報をお調べいたします。",
                    "displayLink": "example.com",
                },
                {
                    "title": "子育て相談・医療機関検索について",
                    "link": "https://example.com/medical-guide",
                    "snippet": "Google Search API Key（GOOGLE_SEARCH_API_KEY）とSearch Engine ID（GOOGLE_SEARCH_ENGINE_ID）を環境変数に設定すると、リアルタイムでの医療機関検索が利用可能になります。",
                    "displayLink": "example.com",
                },
            ]
        elif search_type == "facility":
            demo_results = [
                {
                    "title": f"【{query}】関連の子育て支援施設情報",
                    "link": "https://example.com/facility",
                    "snippet": f"申し訳ございません。現在は検索機能のデモモードです。実際のGoogle Search API設定が完了すると、{query}に関する子育て支援施設の詳細情報をお調べいたします。",
                    "displayLink": "example.com",
                }
            ]
        else:
            demo_results = [
                {
                    "title": f"【{query}】に関する子育て情報",
                    "link": "https://example.com/general",
                    "snippet": f"申し訳ございません。現在は検索機能のデモモードです。実際のGoogle Search API設定が完了すると、{query}に関する最新情報をリアルタイムでお調べいたします。",
                    "displayLink": "example.com",
                },
                {
                    "title": "GenieUs検索機能について",
                    "link": "https://example.com/search-info",
                    "snippet": "Google Custom Search APIを設定することで、医療機関、子育て施設、イベント情報など、様々な子育て関連情報をリアルタイムで検索できるようになります。",
                    "displayLink": "example.com",
                },
            ]

        return demo_results
