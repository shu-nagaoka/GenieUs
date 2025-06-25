"""記録管理Tool - UseCase層の薄いラッパー"""

import logging
from typing import Any

from google.adk.tools import FunctionTool

from src.application.usecases.record_management_usecase import RecordManagementUseCase


def create_record_management_tool(
    record_management_usecase: RecordManagementUseCase,
    logger: logging.Logger,
) -> FunctionTool:
    """記録管理ツール作成（薄いアダプター）

    Args:
        record_management_usecase: 記録管理UseCase
        logger: ロガー（DIコンテナから注入）

    Returns:
        FunctionTool: ADK用記録管理ツール

    """
    logger.info("記録管理ツール作成開始")

    def manage_child_records(
        operation: str,
        child_id: str = "default_child",
        event_type: str = "",
        description: str = "",
        days_back: int = 7,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """子どもの記録管理操作

        Args:
            operation: 操作タイプ（save, get, patterns）
            child_id: 子どものID（デフォルト: "default_child"）
            event_type: イベントタイプ（feeding, sleep, mood等）
            description: 記録の説明（save時に必要）
            days_back: 取得する過去の日数（get時）
            **kwargs: 追加パラメータ

        Returns:
            Dict[str, Any]: 操作結果

        """
        try:
            logger.info(
                f"記録管理ツール実行開始: operation={operation}, child_id={child_id}, event_type={event_type}",
            )

            if operation == "save":
                # 記録保存
                if not description:
                    return _create_error_response(operation, "記録の説明が必要です")

                # 同期関数なので awaitは使えない、適切なラッパーが必要
                # ここでは簡易的な応答を返す
                return {
                    "success": True,
                    "response": "記録保存機能は準備中です。WebUIまたはAPIを通じて記録を追加してください。",
                    "metadata": {
                        "operation": operation,
                        "child_id": child_id,
                        "event_type": event_type,
                    },
                }

            elif operation == "get":
                # 記録取得（同様に簡易応答）
                return {
                    "success": True,
                    "response": f"記録取得機能は準備中です。{days_back}日間の{event_type or '全ての'}記録を確認できます。",
                    "metadata": {
                        "operation": operation,
                        "child_id": child_id,
                        "event_type": event_type,
                        "days_back": days_back,
                    },
                }

            elif operation == "patterns":
                # パターン分析（同様に簡易応答）
                analysis_days = kwargs.get("analysis_days", 30)
                return {
                    "success": True,
                    "response": _create_pattern_analysis_response(child_id, analysis_days),
                    "metadata": {
                        "operation": operation,
                        "child_id": child_id,
                        "analysis_days": analysis_days,
                    },
                }

            else:
                return _create_error_response(operation, f"サポートされていない操作です: {operation}")

        except Exception as e:
            logger.error(f"記録管理ツール実行エラー: {e}")
            return _create_error_response(operation, f"記録管理中にエラーが発生しました: {e!s}")

    def _create_pattern_analysis_response(child_id: str, analysis_days: int) -> str:
        """パターン分析結果の自然言語レスポンス"""
        return f"""
        お子さん（ID: {child_id}）の過去{analysis_days}日間の記録パターンを分析中です。

        📊 分析結果:
        ・記録データが蓄積されると、以下のパターンが検出できます
        ・食事・睡眠・気分などの周期的な変化
        ・成長に伴う行動パターンの変化
        ・環境要因との相関関係

        💡 現在の状況:
        記録管理システムが準備中のため、実際のパターン分析は後日提供されます。
        継続的に記録を蓄積することで、より詳細な分析が可能になります。
        """.strip()

    def _create_error_response(operation: str, error_message: str) -> dict[str, Any]:
        """エラーレスポンス作成"""
        return {
            "success": False,
            "response": f"記録{operation}操作でエラーが発生しました: {error_message}",
            "metadata": {"operation": operation, "error": error_message},
        }

    logger.info("記録管理ツール作成完了")
    return FunctionTool(func=manage_child_records)
