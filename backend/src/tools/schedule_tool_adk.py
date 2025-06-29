"""スケジュール管理ツール - ADK FunctionTool版

ADKと統合されたスケジュール管理機能
"""

import logging
from datetime import datetime, timedelta
from typing import Any

from google.adk.tools import FunctionTool
from src.application.usecases.schedule_event_usecase import ScheduleEventUseCase


def create_schedule_tool(schedule_usecase: ScheduleEventUseCase, logger: logging.Logger) -> FunctionTool:
    """ADK FunctionTool形式のスケジュール管理ツールを作成"""

    async def manage_schedules(
        action: str,
        user_id: str,
        title: str = None,
        description: str = None,
        start_datetime: str = None,
        end_datetime: str = None,
        event_type: str = "other",
        location: str = None,
        notes: str = None,
        schedule_id: str = None,
        start_date: str = None,
        end_date: str = None,
        **kwargs
    ) -> dict[str, Any]:
        """スケジュール管理機能の統合エントリーポイント
        
        Args:
            action: 実行するアクション ("create", "get", "update", "delete", "get_today")
            user_id: ユーザーID
            title: 予定のタイトル (create/update時)
            description: 予定の説明 (create/update時)
            start_datetime: 開始日時 ISO形式 (create/update時)
            end_datetime: 終了日時 ISO形式 (create/update時)
            event_type: 予定の種類 ("medical", "outing", "school", "other")
            location: 場所 (create/update時)
            notes: メモ (create/update時)
            schedule_id: スケジュールID (update/delete時)
            start_date: 取得開始日 YYYY-MM-DD形式 (get時)
            end_date: 取得終了日 YYYY-MM-DD形式 (get時)
        """
        try:
            logger.info(f"🗓️ スケジュール管理ツール実行: {action} (user_id: {user_id})")
            
            if action == "create":
                return await _create_schedule(
                    schedule_usecase, logger, user_id, title, description,
                    start_datetime, end_datetime, event_type, location, notes
                )
            elif action == "get":
                return await _get_schedules(
                    schedule_usecase, logger, user_id, start_date, end_date
                )
            elif action == "update":
                return await _update_schedule(
                    schedule_usecase, logger, user_id, schedule_id, title, 
                    description, start_datetime, end_datetime, location, notes
                )
            elif action == "delete":
                return await _delete_schedule(
                    schedule_usecase, logger, user_id, schedule_id
                )
            elif action == "get_today":
                return await _get_today_schedules(
                    schedule_usecase, logger, user_id
                )
            else:
                raise ValueError(f"未対応のアクション: {action}")
                
        except Exception as e:
            error_msg = f"スケジュール管理エラー ({action}): {e}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "details": str(e)
            }

    # FunctionToolとして返す
    return FunctionTool(
        func=manage_schedules
    )


async def _create_schedule(
    schedule_usecase: ScheduleEventUseCase,
    logger: logging.Logger,
    user_id: str,
    title: str,
    description: str,
    start_datetime: str,
    end_datetime: str,
    event_type: str,
    location: str,
    notes: str
) -> dict[str, Any]:
    """予定作成"""
    if not title or not start_datetime:
        return {
            "success": False,
            "error": "タイトルと開始日時は必須です"
        }
    
    event_data = {
        "title": title,
        "description": description or "",
        "start_datetime": start_datetime,
        "end_datetime": end_datetime,
        "event_type": event_type,
        "location": location or "",
        "notes": notes or "",
    }
    
    response = await schedule_usecase.create_schedule_event(user_id, event_data)
    
    if response.get("success"):
        return {
            "success": True,
            "message": "予定を作成しました",
            "schedule_id": response.get("id"),
            "schedule": response.get("data")
        }
    else:
        return {
            "success": False,
            "error": response.get("message", "予定の作成に失敗しました")
        }


async def _get_schedules(
    schedule_usecase: ScheduleEventUseCase,
    logger: logging.Logger,
    user_id: str,
    start_date: str,
    end_date: str
) -> dict[str, Any]:
    """予定一覧取得"""
    # デフォルト期間設定
    if not start_date:
        start_date = datetime.now().strftime("%Y-%m-%d")
    if not end_date:
        end_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
    
    # フィルター設定（日付範囲）
    filters = {
        "start_date": start_date,
        "end_date": end_date
    }
    
    response = await schedule_usecase.get_schedule_events(user_id, filters)
    
    if response.get("success"):
        schedules_data = response.get("data", [])
        
        return {
            "success": True,
            "schedules": schedules_data,
            "total_count": len(schedules_data),
            "period": f"{start_date} から {end_date}"
        }
    else:
        return {
            "success": False,
            "error": response.get("message", "予定一覧の取得に失敗しました")
        }


async def _update_schedule(
    schedule_usecase: ScheduleEventUseCase,
    logger: logging.Logger,
    user_id: str,
    schedule_id: str,
    title: str,
    description: str,
    start_datetime: str,
    end_datetime: str,
    location: str,
    notes: str
) -> dict[str, Any]:
    """予定更新"""
    if not schedule_id:
        return {
            "success": False,
            "error": "スケジュールIDは必須です"
        }
    
    update_data = {}
    if title is not None:
        update_data["title"] = title
    if description is not None:
        update_data["description"] = description
    if start_datetime is not None:
        update_data["start_datetime"] = start_datetime
    if end_datetime is not None:
        update_data["end_datetime"] = end_datetime
    if location is not None:
        update_data["location"] = location
    if notes is not None:
        update_data["notes"] = notes
    
    response = await schedule_usecase.update_schedule_event(user_id, schedule_id, update_data)
    
    if response.get("success"):
        return {
            "success": True,
            "message": "予定を更新しました",
            "schedule": response.get("data")
        }
    else:
        return {
            "success": False,
            "error": response.get("message", "予定の更新に失敗しました")
        }


async def _delete_schedule(
    schedule_usecase: ScheduleEventUseCase,
    logger: logging.Logger,
    user_id: str,
    schedule_id: str
) -> dict[str, Any]:
    """予定削除"""
    if not schedule_id:
        return {
            "success": False,
            "error": "スケジュールIDは必須です"
        }
    
    response = await schedule_usecase.delete_schedule_event(user_id, schedule_id)
    
    if response.get("success"):
        return {
            "success": True,
            "message": "予定を削除しました"
        }
    else:
        return {
            "success": False,
            "error": response.get("message", "予定の削除に失敗しました")
        }


async def _get_today_schedules(
    schedule_usecase: ScheduleEventUseCase,
    logger: logging.Logger,
    user_id: str
) -> dict[str, Any]:
    """今日の予定取得"""
    today = datetime.now().strftime("%Y-%m-%d")
    
    # 今日の日付でフィルター
    filters = {
        "start_date": today,
        "end_date": today
    }
    
    response = await schedule_usecase.get_schedule_events(user_id, filters)
    
    if response.get("success"):
        schedules_data = response.get("data", [])
        
        # 時間順にソート
        schedules_data.sort(key=lambda x: x.get("start_datetime", ""))
        
        return {
            "success": True,
            "today_schedules": schedules_data,
            "count": len(schedules_data),
            "date": today,
            "message": f"今日は{len(schedules_data)}件の予定があります"
        }
    else:
        return {
            "success": False,
            "error": response.get("message", "今日の予定取得に失敗しました")
        }