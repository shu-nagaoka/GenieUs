"""成長記録管理ツール - ADK FunctionTool版

ADKと統合された成長記録管理機能
"""

import logging
from datetime import datetime
from typing import Any

from google.adk.tools import FunctionTool
from src.application.usecases.growth_record_usecase import GrowthRecordUseCase


def create_growth_record_tool(growth_record_usecase: GrowthRecordUseCase, logger: logging.Logger) -> FunctionTool:
    """ADK FunctionTool形式の成長記録管理ツールを作成"""

    async def manage_growth_records(
        action: str,
        user_id: str,
        child_name: str = None,
        title: str = None,
        description: str = None,
        date: str = None,
        record_type: str = "general",
        height: float = None,
        weight: float = None,
        notes: str = None,
        record_id: str = None,
        start_date: str = None,
        end_date: str = None,
        **kwargs
    ) -> dict[str, Any]:
        """成長記録管理機能の統合エントリーポイント
        
        Args:
            action: 実行するアクション ("create", "get", "update", "delete", "get_list")
            user_id: ユーザーID
            child_name: お子さんの名前 (create/update時)
            title: 記録のタイトル (create/update時)
            description: 記録の詳細説明 (create/update時)
            date: 記録日付 YYYY-MM-DD形式 (create/update時)
            record_type: 記録タイプ ("body_growth", "language_growth", "skills", "general")
            height: 身長 cm (body_growth時)
            weight: 体重 kg (body_growth時)
            notes: メモ (create/update時)
            record_id: 記録ID (update/delete/get時)
            start_date: 取得開始日 (get_list時)
            end_date: 取得終了日 (get_list時)
        """
        try:
            logger.info(f"📊 成長記録管理ツール実行: {action} (user_id: {user_id})")
            
            if action == "create":
                return await _create_growth_record(
                    growth_record_usecase, logger, user_id, child_name, title,
                    description, date, record_type, height, weight, notes
                )
            elif action == "get":
                return await _get_growth_record(
                    growth_record_usecase, logger, user_id, record_id
                )
            elif action == "get_list":
                return await _get_growth_records(
                    growth_record_usecase, logger, user_id, start_date, end_date
                )
            elif action == "update":
                return await _update_growth_record(
                    growth_record_usecase, logger, user_id, record_id, title,
                    description, date, record_type, height, weight, notes
                )
            elif action == "delete":
                return await _delete_growth_record(
                    growth_record_usecase, logger, user_id, record_id
                )
            else:
                raise ValueError(f"未対応のアクション: {action}")

        except Exception as e:
            error_msg = f"成長記録管理エラー ({action}): {e}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "details": str(e)
            }

    return FunctionTool(
        func=manage_growth_records
    )


async def _create_growth_record(
    growth_record_usecase: GrowthRecordUseCase,
    logger: logging.Logger,
    user_id: str,
    child_name: str,
    title: str,
    description: str,
    date: str,
    record_type: str,
    height: float,
    weight: float,
    notes: str
) -> dict[str, Any]:
    """成長記録作成"""
    if not title:
        return {
            "success": False,
            "error": "タイトルは必須です"
        }
    
    # 日付未指定時は今日の日付を使用
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")
    
    record_data = {
        "child_name": child_name or "",
        "title": title,
        "description": description or "",
        "date": date,
        "type": record_type,
        "notes": notes or "",
    }
    
    # 身体測定データがある場合
    if record_type == "body_growth" and (height is not None or weight is not None):
        measurements = {}
        if height is not None:
            measurements["height"] = height
        if weight is not None:
            measurements["weight"] = weight
        record_data["measurements"] = measurements
    
    response = await growth_record_usecase.create_growth_record(user_id, record_data)
    
    if response.get("success"):
        return {
            "success": True,
            "message": "成長記録を作成しました",
            "record_id": response.get("id"),
            "record": response.get("data")
        }
    else:
        return {
            "success": False,
            "error": response.get("message", "成長記録の作成に失敗しました")
        }


async def _get_growth_record(
    growth_record_usecase: GrowthRecordUseCase,
    logger: logging.Logger,
    user_id: str,
    record_id: str
) -> dict[str, Any]:
    """特定の成長記録取得"""
    if not record_id:
        return {
            "success": False,
            "error": "記録IDは必須です"
        }
    
    response = await growth_record_usecase.get_growth_record(user_id, record_id)
    
    if response.get("success"):
        return {
            "success": True,
            "record": response.get("data")
        }
    else:
        return {
            "success": False,
            "error": response.get("message", "成長記録の取得に失敗しました")
        }


async def _get_growth_records(
    growth_record_usecase: GrowthRecordUseCase,
    logger: logging.Logger,
    user_id: str,
    start_date: str,
    end_date: str
) -> dict[str, Any]:
    """成長記録一覧取得"""
    # フィルター設定
    filters = {}
    if start_date:
        filters["start_date"] = start_date
    if end_date:
        filters["end_date"] = end_date
    
    response = await growth_record_usecase.get_growth_records(user_id, filters)
    
    if response.get("success"):
        records_data = response.get("data", [])
        
        return {
            "success": True,
            "records": records_data,
            "total_count": len(records_data),
            "period": f"{start_date or '開始'} から {end_date or '終了'}"
        }
    else:
        return {
            "success": False,
            "error": response.get("message", "成長記録一覧の取得に失敗しました")
        }


async def _update_growth_record(
    growth_record_usecase: GrowthRecordUseCase,
    logger: logging.Logger,
    user_id: str,
    record_id: str,
    title: str,
    description: str,
    date: str,
    record_type: str,
    height: float,
    weight: float,
    notes: str
) -> dict[str, Any]:
    """成長記録更新"""
    if not record_id:
        return {
            "success": False,
            "error": "記録IDは必須です"
        }
    
    update_data = {}
    if title is not None:
        update_data["title"] = title
    if description is not None:
        update_data["description"] = description
    if date is not None:
        update_data["date"] = date
    if record_type is not None:
        update_data["type"] = record_type
    if notes is not None:
        update_data["notes"] = notes
    
    # 身体測定データがある場合
    if record_type == "body_growth" and (height is not None or weight is not None):
        measurements = {}
        if height is not None:
            measurements["height"] = height
        if weight is not None:
            measurements["weight"] = weight
        update_data["measurements"] = measurements
    
    response = await growth_record_usecase.update_growth_record(user_id, record_id, update_data)
    
    if response.get("success"):
        return {
            "success": True,
            "message": "成長記録を更新しました",
            "record": response.get("data")
        }
    else:
        return {
            "success": False,
            "error": response.get("message", "成長記録の更新に失敗しました")
        }


async def _delete_growth_record(
    growth_record_usecase: GrowthRecordUseCase,
    logger: logging.Logger,
    user_id: str,
    record_id: str
) -> dict[str, Any]:
    """成長記録削除"""
    if not record_id:
        return {
            "success": False,
            "error": "記録IDは必須です"
        }
    
    response = await growth_record_usecase.delete_growth_record(user_id, record_id)
    
    if response.get("success"):
        return {
            "success": True,
            "message": "成長記録を削除しました"
        }
    else:
        return {
            "success": False,
            "error": response.get("message", "成長記録の削除に失敗しました")
        }