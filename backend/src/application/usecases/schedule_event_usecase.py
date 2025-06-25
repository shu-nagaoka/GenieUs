"""予定イベント管理UseCase"""

import logging
from typing import Dict, Any, List, Optional

from src.domain.entities import ScheduleEvent


class ScheduleEventUseCase:
    """予定イベント管理のビジネスロジック"""

    def __init__(self, schedule_event_repository, logger: logging.Logger):
        """
        Args:
            schedule_event_repository: 予定イベントリポジトリ
            logger: ロガー（DIコンテナから注入）
        """
        self.schedule_event_repository = schedule_event_repository
        self.logger = logger

    async def create_schedule_event(self, user_id: str, event_data: dict) -> Dict[str, Any]:
        """予定イベントを作成

        Args:
            user_id: ユーザーID
            event_data: 予定イベントデータ

        Returns:
            Dict[str, Any]: 作成結果
        """
        try:
            self.logger.info(f"予定イベント作成開始: user_id={user_id}")

            # 予定イベントエンティティ作成
            schedule_event = ScheduleEvent.from_dict(user_id, event_data)

            # リポジトリに保存
            result = await self.schedule_event_repository.save_schedule_event(schedule_event)

            self.logger.info(f"予定イベント作成完了: user_id={user_id}, event_id={result.get('event_id')}")
            return {"success": True, "id": result.get("event_id"), "data": schedule_event.to_dict()}

        except Exception as e:
            self.logger.error(f"予定イベント作成エラー: user_id={user_id}, error={e}")
            return {"success": False, "message": f"予定イベントの作成に失敗しました: {str(e)}"}

    async def get_schedule_events(self, user_id: str, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """予定イベント一覧を取得

        Args:
            user_id: ユーザーID
            filters: フィルター条件

        Returns:
            Dict[str, Any]: 取得結果
        """
        try:
            self.logger.info(f"予定イベント取得開始: user_id={user_id}")

            events = await self.schedule_event_repository.get_schedule_events(user_id, filters)

            self.logger.info(f"予定イベント取得完了: user_id={user_id}, count={len(events)}")
            return {"success": True, "data": [event.to_dict() for event in events]}

        except Exception as e:
            self.logger.error(f"予定イベント取得エラー: user_id={user_id}, error={e}")
            return {"success": False, "message": f"予定イベントの取得に失敗しました: {str(e)}"}

    async def get_schedule_event(self, user_id: str, event_id: str) -> Dict[str, Any]:
        """特定の予定イベントを取得

        Args:
            user_id: ユーザーID
            event_id: イベントID

        Returns:
            Dict[str, Any]: 取得結果
        """
        try:
            self.logger.info(f"予定イベント詳細取得開始: user_id={user_id}, event_id={event_id}")

            event = await self.schedule_event_repository.get_schedule_event(user_id, event_id)

            if event:
                self.logger.info(f"予定イベント詳細取得成功: user_id={user_id}, event_id={event_id}")
                return {"success": True, "data": event.to_dict()}
            else:
                return {"success": False, "message": "予定が見つかりません"}

        except Exception as e:
            self.logger.error(f"予定イベント詳細取得エラー: user_id={user_id}, event_id={event_id}, error={e}")
            return {"success": False, "message": f"予定イベントの取得に失敗しました: {str(e)}"}

    async def update_schedule_event(self, user_id: str, event_id: str, update_data: dict) -> Dict[str, Any]:
        """予定イベントを更新

        Args:
            user_id: ユーザーID
            event_id: イベントID
            update_data: 更新データ

        Returns:
            Dict[str, Any]: 更新結果
        """
        try:
            self.logger.info(f"予定イベント更新開始: user_id={user_id}, event_id={event_id}")

            # 既存イベントを取得
            existing_event = await self.schedule_event_repository.get_schedule_event(user_id, event_id)
            if not existing_event:
                return {"success": False, "message": "予定が見つかりません"}

            # 更新データをマージ
            updated_data = existing_event.to_dict()
            updated_data.update(update_data)

            # エンティティ作成して保存
            updated_event = ScheduleEvent.from_dict(user_id, updated_data)
            result = await self.schedule_event_repository.update_schedule_event(updated_event)

            self.logger.info(f"予定イベント更新完了: user_id={user_id}, event_id={event_id}")
            return {"success": True, "data": updated_event.to_dict()}

        except Exception as e:
            self.logger.error(f"予定イベント更新エラー: user_id={user_id}, event_id={event_id}, error={e}")
            return {"success": False, "message": f"予定イベントの更新に失敗しました: {str(e)}"}

    async def delete_schedule_event(self, user_id: str, event_id: str) -> Dict[str, Any]:
        """予定イベントを削除

        Args:
            user_id: ユーザーID
            event_id: イベントID

        Returns:
            Dict[str, Any]: 削除結果
        """
        try:
            self.logger.info(f"予定イベント削除開始: user_id={user_id}, event_id={event_id}")

            result = await self.schedule_event_repository.delete_schedule_event(user_id, event_id)

            if result:
                self.logger.info(f"予定イベント削除完了: user_id={user_id}, event_id={event_id}")
                return {"success": True, "message": "予定を削除しました", "deleted_data": result.to_dict()}
            else:
                return {"success": False, "message": "予定が見つかりません"}

        except Exception as e:
            self.logger.error(f"予定イベント削除エラー: user_id={user_id}, event_id={event_id}, error={e}")
            return {"success": False, "message": f"予定イベントの削除に失敗しました: {str(e)}"}

    async def update_schedule_status(self, user_id: str, event_id: str, status: str) -> Dict[str, Any]:
        """予定のステータスを更新

        Args:
            user_id: ユーザーID
            event_id: イベントID
            status: 新しいステータス

        Returns:
            Dict[str, Any]: 更新結果
        """
        try:
            self.logger.info(f"予定ステータス更新開始: user_id={user_id}, event_id={event_id}, status={status}")

            # ステータス値の妥当性チェック
            valid_statuses = ["upcoming", "completed", "cancelled"]
            if status not in valid_statuses:
                return {"success": False, "message": f"無効なステータス: {status}"}

            # 既存イベントを取得
            existing_event = await self.schedule_event_repository.get_schedule_event(user_id, event_id)
            if not existing_event:
                return {"success": False, "message": "予定が見つかりません"}

            # ステータスを更新
            existing_event.status = status
            result = await self.schedule_event_repository.update_schedule_event(existing_event)

            self.logger.info(f"予定ステータス更新完了: user_id={user_id}, event_id={event_id}")
            return {"success": True, "data": existing_event.to_dict()}

        except Exception as e:
            self.logger.error(f"予定ステータス更新エラー: user_id={user_id}, event_id={event_id}, error={e}")
            return {"success": False, "message": f"予定ステータスの更新に失敗しました: {str(e)}"}
