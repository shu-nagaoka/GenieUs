"""成長記録管理Tool - GrowthRecordUseCaseの薄いラッパー"""

import asyncio
import logging
from typing import Any, Dict, List, Optional

from google.adk.tools import FunctionTool

from src.application.usecases.growth_record_usecase import GrowthRecordUseCase


def create_growth_record_tool(
    growth_record_usecase: GrowthRecordUseCase,
    logger: logging.Logger,
) -> FunctionTool:
    """成長記録管理ツール作成（UseCaseのラッパー）

    Args:
        growth_record_usecase: 成長記録UseCase
        logger: ロガー（DIコンテナから注入）

    Returns:
        FunctionTool: ADK用成長記録管理ツール

    """
    logger.info("成長記録管理ツール作成開始")

    def manage_growth_records(
        operation: str,
        user_id: str = "frontend_user",
        child_name: str = "",
        record_id: str = "",
        title: str = "",
        description: str = "",
        date: str = "",
        type: str = "milestone",
        category: str = "",
        value: str = "",
        unit: str = "",
        detected_by: str = "genie",
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """成長記録のCRUD操作

        Args:
            operation: 操作タイプ（create, read, update, delete, list）
            user_id: ユーザーID
            child_name: 子どもの名前
            record_id: 記録ID（update, delete時に必要）
            title: 記録のタイトル
            description: 記録の説明
            date: 記録日付（YYYY-MM-DD形式）
            type: 記録タイプ（body_growth, language_growth, skills等）
            category: カテゴリ
            value: 測定値（必要に応じて）
            unit: 単位（必要に応じて）
            detected_by: 記録者（genie or parent）
            **kwargs: 追加パラメータ

        Returns:
            Dict[str, Any]: 操作結果

        """
        try:
            logger.info(f"成長記録ツール実行開始: operation={operation}, user_id={user_id}, child_name={child_name}")

            # 非同期関数を同期的に実行するためのヘルパー
            def run_async(coro):
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        # 既存のループがある場合は新しいタスクとして実行
                        import concurrent.futures

                        with concurrent.futures.ThreadPoolExecutor() as executor:
                            future = executor.submit(asyncio.run, coro)
                            return future.result(timeout=30)
                    else:
                        return loop.run_until_complete(coro)
                except RuntimeError:
                    # ループが存在しない場合は新しく作成
                    return asyncio.run(coro)

            if operation == "create":
                # 成長記録作成
                if not child_name or not title or not description:
                    return _create_error_response(operation, "子どもの名前、タイトル、説明が必要です")

                record_data = {
                    "child_name": child_name,
                    "title": title,
                    "description": description,
                    "date": date or _get_today_date(),
                    "type": type,
                    "category": category,
                    "value": value,
                    "unit": unit,
                    "detected_by": detected_by,
                }

                result = run_async(growth_record_usecase.create_growth_record(user_id, record_data))

                if result.get("success"):
                    return {
                        "success": True,
                        "response": f"✅ {child_name}さんの成長記録「{title}」を保存しました！",
                        "data": result.get("data"),
                        "metadata": {"operation": operation, "record_id": result.get("id")},
                    }
                else:
                    return _create_error_response(operation, result.get("message", "記録の作成に失敗しました"))

            elif operation == "list":
                # 成長記録一覧取得
                filters = {}
                if child_name:
                    filters["child_name"] = child_name
                if type and type != "all":
                    filters["type"] = type
                if category:
                    filters["category"] = category

                result = run_async(growth_record_usecase.get_growth_records(user_id, filters))

                if result.get("success"):
                    records = result.get("data", [])
                    return {
                        "success": True,
                        "response": _format_records_list(records, child_name),
                        "data": records,
                        "metadata": {"operation": operation, "count": len(records)},
                    }
                else:
                    return _create_error_response(operation, result.get("message", "記録の取得に失敗しました"))

            elif operation == "read":
                # 特定の成長記録取得
                if not record_id:
                    return _create_error_response(operation, "記録IDが必要です")

                result = run_async(growth_record_usecase.get_growth_record(user_id, record_id))

                if result.get("success"):
                    record = result.get("data")
                    return {
                        "success": True,
                        "response": _format_single_record(record),
                        "data": record,
                        "metadata": {"operation": operation, "record_id": record_id},
                    }
                else:
                    return _create_error_response(operation, result.get("message", "記録が見つかりません"))

            elif operation == "update":
                # 成長記録更新
                if not record_id:
                    return _create_error_response(operation, "記録IDが必要です")

                update_data = {}
                if title:
                    update_data["title"] = title
                if description:
                    update_data["description"] = description
                if date:
                    update_data["date"] = date
                if type:
                    update_data["type"] = type
                if category:
                    update_data["category"] = category
                if value:
                    update_data["value"] = value
                if unit:
                    update_data["unit"] = unit

                if not update_data:
                    return _create_error_response(operation, "更新する内容が指定されていません")

                result = run_async(growth_record_usecase.update_growth_record(user_id, record_id, update_data))

                if result.get("success"):
                    return {
                        "success": True,
                        "response": f"✅ 成長記録を更新しました（ID: {record_id}）",
                        "data": result.get("data"),
                        "metadata": {"operation": operation, "record_id": record_id},
                    }
                else:
                    return _create_error_response(operation, result.get("message", "記録の更新に失敗しました"))

            elif operation == "delete":
                # 成長記録削除
                if not record_id:
                    return _create_error_response(operation, "記録IDが必要です")

                result = run_async(growth_record_usecase.delete_growth_record(user_id, record_id))

                if result.get("success"):
                    return {
                        "success": True,
                        "response": f"✅ 成長記録を削除しました（ID: {record_id}）",
                        "metadata": {"operation": operation, "record_id": record_id},
                    }
                else:
                    return _create_error_response(operation, result.get("message", "記録の削除に失敗しました"))

            else:
                return _create_error_response(operation, f"サポートされていない操作です: {operation}")

        except Exception as e:
            logger.error(f"成長記録ツール実行エラー: {e}")
            return _create_error_response(operation, f"処理中にエラーが発生しました: {e!s}")

    def _format_records_list(records: List[Dict], child_name_filter: str = "") -> str:
        """記録一覧の自然言語フォーマット"""
        if not records:
            filter_text = f"（{child_name_filter}さんの）" if child_name_filter else ""
            return f"📋 成長記録{filter_text}はまだありません。最初の記録を作成してみましょう！"

        response_parts = []
        if child_name_filter:
            response_parts.append(f"📊 {child_name_filter}さんの成長記録（{len(records)}件）:")
        else:
            response_parts.append(f"📊 成長記録一覧（{len(records)}件）:")

        # 最新の5件を表示
        for i, record in enumerate(records[:5]):
            date = record.get("date", "")
            title = record.get("title", "")
            type_label = _get_type_label(record.get("type", ""))
            response_parts.append(f"  {i + 1}. {date} - {title} ({type_label})")

        if len(records) > 5:
            response_parts.append(f"  ...他{len(records) - 5}件の記録があります")

        return "\n".join(response_parts)

    def _format_single_record(record: Dict) -> str:
        """単一記録の詳細フォーマット"""
        if not record:
            return "記録が見つかりませんでした。"

        parts = [
            f"📝 成長記録詳細",
            f"",
            f"👶 お子さん: {record.get('child_name', '')}",
            f"📅 日付: {record.get('date', '')}",
            f"🏷️ タイトル: {record.get('title', '')}",
            f"📋 説明: {record.get('description', '')}",
            f"🎯 タイプ: {_get_type_label(record.get('type', ''))}",
        ]

        if record.get("category"):
            parts.append(f"📂 カテゴリ: {record.get('category')}")

        if record.get("value") and record.get("unit"):
            parts.append(f"📏 測定値: {record.get('value')} {record.get('unit')}")

        parts.append(f"👤 記録者: {record.get('detected_by', 'unknown')}")

        return "\n".join(parts)

    def _get_type_label(record_type: str) -> str:
        """記録タイプのラベル変換"""
        type_labels = {
            "body_growth": "からだの成長",
            "language_growth": "ことばの成長",
            "skills": "できること",
            "social_skills": "お友達との関わり",
            "hobbies": "習い事・特技",
            "life_skills": "生活スキル",
            "milestone": "マイルストーン",
            "photo": "写真記録",
        }
        return type_labels.get(record_type, record_type)

    def _get_today_date() -> str:
        """今日の日付を取得"""
        from datetime import datetime

        return datetime.now().strftime("%Y-%m-%d")

    def _create_error_response(operation: str, error_message: str) -> Dict[str, Any]:
        """エラーレスポンス作成"""
        return {
            "success": False,
            "response": f"❌ 成長記録{operation}操作でエラーが発生しました: {error_message}",
            "metadata": {"operation": operation, "error": error_message},
        }

    logger.info("成長記録管理ツール作成完了")
    return FunctionTool(func=manage_growth_records)
