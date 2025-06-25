import logging
from typing import Any
from google.adk.tools import FunctionTool
from src.application.usecases.web_search_usecase import WebSearchUseCase
from src.tools.common_response_formatter import ChildcareResponseFormatter


def create_web_search_tool(web_search_usecase: WebSearchUseCase, logger: logging.Logger):
    """Web検索ツール作成（薄いアダプター）"""
    logger.info("Web検索ツール作成開始")

    async def search_web_information(
        query: str = "",  # 検索クエリ
        location: str = "",  # 地域指定（オプション）
        search_type: str = "general",  # 検索タイプ（general, medical, facility, service, etc.）
        **kwargs: Any,
    ) -> dict[str, Any]:
        """子育てに関する情報をWeb検索で取得

        Args:
            query: 検索したい内容
            location: 地域指定（例：「東京都渋谷区」「大阪市」など）
            search_type: 検索タイプ（general, medical, facility, service, event, product）
            **kwargs: 追加のコンテキスト情報

        Returns:
            Dict[str, Any]: 検索結果

        """
        try:
            logger.info(f"🔍 Web検索ツール実行開始: query={query}, location={location}, search_type={search_type}")
            logger.info(f"🔍 検索中... インターネットから最新情報を取得しています")

            # queryが空の場合の処理
            if not query or query.strip() == "":
                logger.info("検索クエリが提供されていません - デモンストレーションモードで実行")
                # デモ用レスポンス
                demo_response = ChildcareResponseFormatter.web_search_success(
                    search_results=[
                        {
                            "title": "検索クエリをお教えください",
                            "url": "https://example.com",
                            "snippet": "具体的な検索内容をお教えいただければ、最新の情報をお調べいたします。",
                            "source": "GenieUs検索システム",
                        }
                    ],
                    search_query=query,
                    location=location,
                    total_results=1,
                    suggestions=["検索したい内容を具体的にお教えください"],
                    search_type=search_type,
                )
                response_dict = demo_response.to_dict()
                logger.info(f"🔧 ツールレスポンス詳細: {response_dict}")
                return response_dict

            logger.info(f"🔍 検索クエリ: {query[:100]}...")
            logger.info(f"📍 地域指定: {location}")
            logger.info(f"🏷️ 検索タイプ: {search_type}")
            logger.info(f"🌐 Google検索API実行中...")

            # UseCaseを通じて検索実行
            search_result = await web_search_usecase.search_childcare_information(
                query=query, location=location, search_type=search_type
            )

            logger.info(
                f"✅ 検索完了: {len(search_result.search_results) if hasattr(search_result, 'search_results') else 0}件の結果を取得"
            )

            # 成功レスポンス作成
            success_response = ChildcareResponseFormatter.web_search_success(
                search_results=search_result.search_results,
                search_query=search_result.search_query,
                location=search_result.location,
                total_results=search_result.total_results,
                suggestions=search_result.suggestions,
                search_type=search_result.search_type,
            )

            response_dict = success_response.to_dict()
            logger.info(f"🎯 Web検索ツール実行成功: 結果{len(search_result.search_results)}件")
            logger.info(f"🔧 ツールレスポンス詳細: {response_dict}")

            return response_dict

        except Exception as e:
            logger.error(f"❌ Web検索ツール実行エラー: {e}")
            logger.error(f"🔍 検索失敗: query={query}, location={location}")

            # エラーレスポンス作成
            error_response = ChildcareResponseFormatter.web_search_error(
                error_message=str(e),
                search_query=query,
                location=location,
                search_type=search_type,
            )

            response_dict = error_response.to_dict()
            logger.info(f"🔧 エラーレスポンス詳細: {response_dict}")

            return response_dict

    # FunctionTool作成
    web_search_tool = FunctionTool(
        name="web_search",
        description="子育てに関する最新情報をインターネット検索で取得します。医療機関、施設、イベント、制度、商品などの情報を地域指定で検索可能。",
        func=search_web_information,
    )

    logger.info("Web検索ツール作成完了")
    return web_search_tool
