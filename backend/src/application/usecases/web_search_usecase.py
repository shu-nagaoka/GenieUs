import logging
from typing import Any, List
from dataclasses import dataclass

from src.application.interface.protocols.web_searcher import WebSearcherProtocol


@dataclass
class WebSearchResult:
    """Web検索結果データクラス"""

    search_results: List[dict[str, Any]]
    search_query: str
    location: str
    total_results: int
    suggestions: List[str]
    search_type: str


class WebSearchUseCase:
    """Web検索のビジネスロジック"""

    def __init__(self, web_searcher: WebSearcherProtocol, logger: logging.Logger) -> None:
        self.web_searcher = web_searcher
        self.logger = logger

    async def search_childcare_information(
        self,
        query: str,
        location: str = "",
        search_type: str = "general",
    ) -> WebSearchResult:
        """子育てに関する情報をWeb検索で取得

        Args:
            query: 検索クエリ
            location: 地域指定
            search_type: 検索タイプ

        Returns:
            WebSearchResult: 検索結果

        """
        try:
            self.logger.info(f"Web検索開始: query={query}, location={location}, search_type={search_type}")

            # ビジネスロジック: 子育て用検索クエリの最適化
            optimized_query = self._optimize_childcare_query(query, location, search_type)

            # Infrastructure層のWeb検索を実行
            raw_results = await self.web_searcher.search_web(
                query=optimized_query,
                num_results=10,
                search_type=search_type,
            )

            # ビジネスロジック: 子育て関連の結果をフィルタリング・ランキング
            filtered_results = self._filter_childcare_relevant_results(raw_results, search_type)

            # ビジネスロジック: 結果の構造化・整理
            structured_results = self._structure_search_results(filtered_results, search_type)

            # ビジネスロジック: 追加提案の生成
            suggestions = self._generate_search_suggestions(query, location, search_type, structured_results)

            result = WebSearchResult(
                search_results=structured_results,
                search_query=optimized_query,
                location=location,
                total_results=len(structured_results),
                suggestions=suggestions,
                search_type=search_type,
            )

            self.logger.info(f"Web検索完了: 結果{len(structured_results)}件")
            return result

        except Exception as e:
            self.logger.error(f"Web検索エラー: {e}")
            raise

    def _optimize_childcare_query(self, query: str, location: str, search_type: str) -> str:
        """子育て用検索クエリの最適化"""
        optimized_query = query

        # 地域指定がある場合は追加
        if location:
            optimized_query = f"{location} {optimized_query}"

        # 検索タイプに応じたキーワード追加
        if search_type == "medical":
            optimized_query += " 小児科 子ども"
        elif search_type == "facility":
            optimized_query += " 子育て 施設"
        elif search_type == "service":
            optimized_query += " 子育て支援 サービス"
        elif search_type == "event":
            optimized_query += " 子ども向け イベント"
        elif search_type == "product":
            optimized_query += " 子育て グッズ"

        self.logger.info(f"クエリ最適化: '{query}' → '{optimized_query}'")
        return optimized_query

    def _filter_childcare_relevant_results(self, raw_results: List[dict], search_type: str) -> List[dict]:
        """子育て関連の結果をフィルタリング"""
        # 子育て関連キーワードでのフィルタリング
        relevant_keywords = [
            "子ども",
            "子育て",
            "育児",
            "幼児",
            "赤ちゃん",
            "乳児",
            "小児",
            "保育",
            "幼稚園",
            "ママ",
            "パパ",
            "親子",
            "家族",
        ]

        filtered_results = []
        for result in raw_results[:10]:  # 上位10件まで
            # タイトルや説明文に子育て関連キーワードが含まれるかチェック
            title = result.get("title", "").lower()
            snippet = result.get("snippet", "").lower()

            is_relevant = any(keyword in title or keyword in snippet for keyword in relevant_keywords)

            # 検索タイプが指定されている場合は、より柔軟に判定
            if search_type != "general" or is_relevant:
                filtered_results.append(result)

        self.logger.info(f"フィルタリング結果: {len(raw_results)}件 → {len(filtered_results)}件")
        return filtered_results

    def _structure_search_results(self, results: List[dict], search_type: str) -> List[dict[str, Any]]:
        """検索結果の構造化"""
        structured_results = []

        for result in results:
            structured_result = {
                "title": result.get("title", "タイトル不明"),
                "url": result.get("link", result.get("url", "")),
                "snippet": result.get("snippet", result.get("description", "説明なし")),
                "source": self._extract_domain(result.get("link", result.get("url", ""))),
                "relevance_score": self._calculate_relevance_score(result, search_type),
            }
            structured_results.append(structured_result)

        # 関連度スコアでソート
        structured_results.sort(key=lambda x: x["relevance_score"], reverse=True)

        return structured_results

    def _extract_domain(self, url: str) -> str:
        """URLからドメインを抽出"""
        try:
            from urllib.parse import urlparse

            parsed = urlparse(url)
            return parsed.netloc
        except Exception:
            return "不明なソース"

    def _calculate_relevance_score(self, result: dict, search_type: str) -> float:
        """関連度スコアの計算"""
        score = 0.5  # 基本スコア

        title = result.get("title", "").lower()
        snippet = result.get("snippet", result.get("description", "")).lower()
        url = result.get("link", result.get("url", "")).lower()

        # 公式サイトや信頼できるドメインにボーナス
        trusted_domains = ["mhlw.go.jp", "city.", "pref.", "go.jp", "or.jp", "jspp.net", "jpeds.or.jp", "kosodate.org"]
        if any(domain in url for domain in trusted_domains):
            score += 0.3

        # 検索タイプ別のキーワードマッチング
        type_keywords = {
            "medical": ["病院", "クリニック", "小児科", "医師", "診療", "医療"],
            "facility": ["センター", "施設", "児童館", "支援", "保育"],
            "service": ["サービス", "支援", "相談", "窓口", "手続き"],
            "event": ["イベント", "教室", "体験", "開催", "参加"],
            "product": ["商品", "グッズ", "用品", "購入", "通販"],
        }

        if search_type in type_keywords:
            keywords = type_keywords[search_type]
            matches = sum(1 for keyword in keywords if keyword in title or keyword in snippet)
            score += matches * 0.1

        return min(score, 1.0)

    def _generate_search_suggestions(
        self, query: str, location: str, search_type: str, results: List[dict]
    ) -> List[str]:
        """検索提案の生成"""
        suggestions = []

        # 基本的な提案
        if search_type == "general":
            suggestions.extend(
                [
                    "より具体的な地域名を教えてください",
                    "特定の種類の施設をお探しですか？",
                    "利用したいサービスの詳細を教えてください",
                ]
            )
        elif search_type == "medical":
            suggestions.extend(
                [
                    "診療科を具体的に指定してみてください",
                    "症状や相談内容を詳しく教えてください",
                    "予約方法や受診時間も調べますか？",
                ]
            )
        elif search_type == "facility":
            suggestions.extend(
                [
                    "利用したい年齢や目的を教えてください",
                    "アクセス方法も調べますか？",
                    "利用料金や申込み方法も知りたいですか？",
                ]
            )

        # 地域がない場合の提案
        if not location:
            suggestions.append("お住まいの地域を教えていただくと、より詳細な情報をお調べできます")

        # 結果が少ない場合の提案
        if len(results) < 3:
            suggestions.append("検索キーワードを変えて、別の表現で調べてみますか？")

        return suggestions[:3]  # 最大3つまで
