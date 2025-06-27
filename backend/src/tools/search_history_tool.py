"""検索履歴記録機能付きGoogle Search Tool

ADK ToolContextを活用して検索クエリと結果を記録する
カスタムGoogle Search ツール実装
"""

import logging
from datetime import datetime
from typing import Any

from google.adk.tools.tool_context import ToolContext
from google.adk.tools import FunctionTool, google_search


def create_search_history_tool(logger: logging.Logger) -> FunctionTool:
    """検索履歴記録機能付きGoogle Search ツール作成"""

    def search_with_history(
        query: str,
        tool_context: ToolContext | None = None,
    ) -> dict[str, Any]:
        """Google検索実行 + 履歴記録機能
        
        Args:
            query: 検索クエリ
            tool_context: ADK ToolContext (自動注入)
            
        Returns:
            dict: 検索結果と履歴情報

        """
        # 検索開始ログ
        logger.info(f"🔍 Google Search開始: query='{query}'")

        search_timestamp = datetime.now().isoformat()

        try:
            # 実際のGoogle検索実行
            search_results = google_search.function(query)

            # 検索履歴をToolContextに記録
            if tool_context:
                # 検索情報をセッション状態に保存
                search_history = tool_context.state.get("search_history", [])

                search_record = {
                    "query": query,
                    "timestamp": search_timestamp,
                    "function_call_id": tool_context.function_call_id,
                    "results_count": len(search_results.get("results", [])) if isinstance(search_results, dict) else 0,
                    "success": True,
                }

                # 検索結果のサマリー情報を追加
                if isinstance(search_results, dict) and "results" in search_results:
                    results = search_results["results"]
                    if results:
                        search_record["accessed_sites"] = [
                            {
                                "title": result.get("title", ""),
                                "url": result.get("url", ""),
                                "domain": result.get("displayLink", ""),
                            }
                            for result in results[:5]  # 上位5件のみ記録
                        ]

                search_history.append(search_record)

                # 履歴は最新100件まで保持
                if len(search_history) > 100:
                    search_history = search_history[-100:]

                tool_context.state["search_history"] = search_history
                tool_context.state["last_search"] = search_record

                logger.info(f"✅ 検索履歴記録完了: function_call_id={tool_context.function_call_id}")

            # レスポンス構築
            response = {
                "search_results": search_results,
                "search_metadata": {
                    "query": query,
                    "timestamp": search_timestamp,
                    "function_call_id": tool_context.function_call_id if tool_context else None,
                    "results_count": len(search_results.get("results", [])) if isinstance(search_results, dict) else 0,
                },
            }

            logger.info(f"🎯 Google Search完了: {response['search_metadata']['results_count']}件の結果")
            return response

        except Exception as e:
            logger.error(f"❌ Google Search エラー: {e!s}")

            # エラーも履歴に記録
            if tool_context:
                search_history = tool_context.state.get("search_history", [])
                error_record = {
                    "query": query,
                    "timestamp": search_timestamp,
                    "function_call_id": tool_context.function_call_id,
                    "success": False,
                    "error": str(e),
                }
                search_history.append(error_record)
                tool_context.state["search_history"] = search_history

            # エラーレスポンス
            return {
                "search_results": None,
                "search_metadata": {
                    "query": query,
                    "timestamp": search_timestamp,
                    "function_call_id": tool_context.function_call_id if tool_context else None,
                    "error": str(e),
                    "success": False,
                },
            }

    # FunctionTool作成（関数を直接渡す）
    return FunctionTool(search_with_history)


def get_search_history(tool_context: ToolContext) -> list[dict[str, Any]]:
    """検索履歴取得
    
    Args:
        tool_context: ADK ToolContext
        
    Returns:
        list: 検索履歴リスト

    """
    return tool_context.state.get("search_history", [])


def get_last_search(tool_context: ToolContext) -> dict[str, Any] | None:
    """最後の検索情報取得
    
    Args:
        tool_context: ADK ToolContext
        
    Returns:
        dict or None: 最後の検索情報

    """
    return tool_context.state.get("last_search")


def clear_search_history(tool_context: ToolContext) -> bool:
    """検索履歴クリア
    
    Args:
        tool_context: ADK ToolContext
        
    Returns:
        bool: 成功可否

    """
    try:
        tool_context.state["search_history"] = []
        tool_context.state.pop("last_search", None)
        return True
    except Exception:
        return False
