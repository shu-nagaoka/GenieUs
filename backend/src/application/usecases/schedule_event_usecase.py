"""予定イベント管理UseCase

コーディング規約準拠:
- Import文ファイル先頭配置
- 型アノテーション完備
- DI注入パターン
- 段階的エラーハンドリング
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from src.application.interface.protocols.schedule_record_repository import ScheduleRecordRepositoryProtocol
from src.domain.entities import ScheduleEvent


@dataclass
class CreateScheduleEventRequest:
    """スケジュールイベント作成リクエスト"""

    user_id: str
    title: str
    date: str | None = None
    time: str | None = None
    event_type: str | None = None
    location: str | None = None
    description: str | None = None
    created_by: str = "genie"


@dataclass
class UpdateScheduleEventRequest:
    """スケジュールイベント更新リクエスト"""

    event_id: str
    user_id: str
    title: str | None = None
    date: str | None = None
    time: str | None = None
    event_type: str | None = None
    location: str | None = None
    description: str | None = None
    status: str | None = None


@dataclass
class SearchScheduleEventsRequest:
    """スケジュールイベント検索リクエスト"""

    user_id: str
    start_date: datetime | None = None
    end_date: datetime | None = None
    event_type: str | None = None
    status: str | None = None
    limit: int = 50
    offset: int = 0


@dataclass
class ScheduleEventResponse:
    """スケジュールイベントレスポンス"""

    success: bool
    schedule_event: dict[str, Any] | None = None
    error: str | None = None


@dataclass
class ScheduleEventListResponse:
    """スケジュールイベント一覧レスポンス"""

    success: bool
    schedule_events: list[dict[str, Any]] | None = None
    total_count: int = 0
    error: str | None = None


class ScheduleEventUseCase:
    """スケジュールイベント管理UseCase

    責務:
    - 個別スケジュールイベントのCRUD操作
    - 日付・時間範囲での検索・フィルタリング機能
    - ステータス管理
    """

    def __init__(
        self,
        schedule_record_repository: ScheduleRecordRepositoryProtocol,
        logger: logging.Logger,
    ):
        """ScheduleEventUseCase初期化

        Args:
            schedule_record_repository: スケジュール記録リポジトリ
            logger: DIコンテナから注入されるロガー
        """
        self.schedule_record_repository = schedule_record_repository
        self.logger = logger

    async def create_schedule_event_new(self, request: CreateScheduleEventRequest) -> ScheduleEventResponse:
        """スケジュールイベント作成

        Args:
            request: スケジュールイベント作成リクエスト

        Returns:
            ScheduleEventResponse: 作成結果
        """
        try:
            self.logger.info(f"📅 スケジュールイベント作成開始: {request.title}")

            # バリデーション
            if not request.user_id.strip():
                return ScheduleEventResponse(success=False, error="user_id is required")

            if not request.title.strip():
                return ScheduleEventResponse(success=False, error="title is required")

            # ScheduleEvent エンティティ作成
            schedule_event = ScheduleEvent(
                user_id=request.user_id,
                title=request.title,
                date=request.date or "",
                time=request.time or "",
                type=request.event_type or "",
                location=request.location,
                description=request.description,
                status="upcoming",
                created_by=request.created_by,
            )

            # リポジトリに保存
            saved_event = await self.schedule_record_repository.create(schedule_event)

            self.logger.info(f"✅ スケジュールイベント作成完了: {saved_event.event_id}")
            return ScheduleEventResponse(success=True, schedule_event=saved_event.to_dict())

        except ValueError as e:
            self.logger.error(f"❌ スケジュールイベントバリデーションエラー: {e}")
            return ScheduleEventResponse(success=False, error=f"Invalid input: {str(e)}")
        except Exception as e:
            self.logger.error(f"❌ スケジュールイベント作成エラー: {e}")
            return ScheduleEventResponse(success=False, error=f"Failed to create schedule event: {str(e)}")

    async def create_schedule_event(self, user_id: str, event_data: dict) -> dict[str, Any]:
        """レガシー互換性のための予定イベント作成メソッド

        Args:
            user_id: ユーザーID
            event_data: 予定イベントデータ

        Returns:
            Dict[str, Any]: 作成結果
        """
        try:
            request = CreateScheduleEventRequest(
                user_id=user_id,
                title=event_data.get("title", ""),
                date=event_data.get("date"),
                time=event_data.get("time"),
                event_type=event_data.get("type") or event_data.get("event_type"),
                location=event_data.get("location"),
                description=event_data.get("description"),
                created_by=event_data.get("created_by", "genie"),
            )

            response = await self.create_schedule_event_new(request)

            if response.success:
                return {"success": True, "id": response.schedule_event["id"], "data": response.schedule_event}
            else:
                return {"success": False, "message": response.error}

        except Exception as e:
            self.logger.error(f"❌ レガシー予定イベント作成エラー: {e}")
            return {"success": False, "message": f"予定イベントの作成に失敗しました: {str(e)}"}

    async def get_schedule_event_new(self, event_id: str) -> ScheduleEventResponse:
        """スケジュールイベント取得

        Args:
            event_id: スケジュールイベントID

        Returns:
            ScheduleEventResponse: 取得結果
        """
        try:
            self.logger.info(f"🔍 スケジュールイベント取得: {event_id}")

            schedule_event = await self.schedule_record_repository.get_by_id(event_id)

            if not schedule_event:
                return ScheduleEventResponse(success=False, error="Schedule event not found")

            return ScheduleEventResponse(success=True, schedule_event=schedule_event.to_dict())

        except Exception as e:
            self.logger.error(f"❌ スケジュールイベント取得エラー: {e}")
            return ScheduleEventResponse(success=False, error=f"Failed to get schedule event: {str(e)}")

    async def update_schedule_event_new(self, request: UpdateScheduleEventRequest) -> ScheduleEventResponse:
        """スケジュールイベント更新

        Args:
            request: スケジュールイベント更新リクエスト

        Returns:
            ScheduleEventResponse: 更新結果
        """
        try:
            self.logger.info(f"📝 スケジュールイベント更新: {request.event_id}")

            # 既存イベント取得
            schedule_event = await self.schedule_record_repository.get_by_id(request.event_id)
            if not schedule_event:
                return ScheduleEventResponse(success=False, error="Schedule event not found")

            # ユーザー権限チェック
            if schedule_event.user_id != request.user_id:
                return ScheduleEventResponse(success=False, error="Access denied")

            # 更新データ適用
            if request.title is not None:
                schedule_event.title = request.title
            if request.date is not None:
                schedule_event.date = request.date
            if request.time is not None:
                schedule_event.time = request.time
            if request.event_type is not None:
                schedule_event.type = request.event_type
            if request.location is not None:
                schedule_event.location = request.location
            if request.description is not None:
                schedule_event.description = request.description
            if request.status is not None:
                schedule_event.status = request.status

            # リポジトリに保存
            updated_event = await self.schedule_record_repository.update(schedule_event)

            self.logger.info(f"✅ スケジュールイベント更新完了: {updated_event.event_id}")
            return ScheduleEventResponse(success=True, schedule_event=updated_event.to_dict())

        except ValueError as e:
            self.logger.error(f"❌ スケジュールイベント更新バリデーションエラー: {e}")
            return ScheduleEventResponse(success=False, error=f"Invalid input: {str(e)}")
        except Exception as e:
            self.logger.error(f"❌ スケジュールイベント更新エラー: {e}")
            return ScheduleEventResponse(success=False, error=f"Failed to update schedule event: {str(e)}")

    async def delete_schedule_event_new(self, event_id: str, user_id: str) -> ScheduleEventResponse:
        """スケジュールイベント削除

        Args:
            event_id: スケジュールイベントID
            user_id: ユーザーID

        Returns:
            ScheduleEventResponse: 削除結果
        """
        try:
            self.logger.info(f"🗑️ スケジュールイベント削除: {event_id}")

            # 既存イベント取得
            schedule_event = await self.schedule_record_repository.get_by_id(event_id)
            if not schedule_event:
                return ScheduleEventResponse(success=False, error="Schedule event not found")

            # ユーザー権限チェック
            if schedule_event.user_id != user_id:
                return ScheduleEventResponse(success=False, error="Access denied")

            success = await self.schedule_record_repository.delete(event_id)

            if not success:
                return ScheduleEventResponse(success=False, error="Schedule event not found or failed to delete")

            self.logger.info(f"✅ スケジュールイベント削除完了: {event_id}")
            return ScheduleEventResponse(success=True)

        except Exception as e:
            self.logger.error(f"❌ スケジュールイベント削除エラー: {e}")
            return ScheduleEventResponse(success=False, error=f"Failed to delete schedule event: {str(e)}")

    async def search_schedule_events(self, request: SearchScheduleEventsRequest) -> ScheduleEventListResponse:
        """スケジュールイベント検索

        Args:
            request: 検索リクエスト

        Returns:
            ScheduleEventListResponse: 検索結果
        """
        try:
            self.logger.info(f"🔍 スケジュールイベント検索: user_id={request.user_id}")

            schedule_events = await self.schedule_record_repository.search(
                user_id=request.user_id,
                start_date=request.start_date,
                end_date=request.end_date,
                event_type=request.event_type,
                status=request.status,
                limit=request.limit,
                offset=request.offset,
            )

            total_count = await self.schedule_record_repository.count(
                user_id=request.user_id,
                start_date=request.start_date,
                end_date=request.end_date,
                event_type=request.event_type,
                status=request.status,
            )

            return ScheduleEventListResponse(
                success=True,
                schedule_events=[event.to_dict() for event in schedule_events],
                total_count=total_count,
            )

        except Exception as e:
            self.logger.error(f"❌ スケジュールイベント検索エラー: {e}")
            return ScheduleEventListResponse(success=False, error=f"Failed to search schedule events: {str(e)}")

    async def get_upcoming_events(self, user_id: str, days: int = 30) -> ScheduleEventListResponse:
        """今後の予定取得

        Args:
            user_id: ユーザーID
            days: 今後何日分を取得するか

        Returns:
            ScheduleEventListResponse: 今後の予定
        """
        try:
            self.logger.info(f"📅 今後の予定取得: user_id={user_id}")

            schedule_events = await self.schedule_record_repository.get_upcoming_events(user_id, days)

            return ScheduleEventListResponse(
                success=True,
                schedule_events=[event.to_dict() for event in schedule_events],
                total_count=len(schedule_events),
            )

        except Exception as e:
            self.logger.error(f"❌ 今後の予定取得エラー: {e}")
            return ScheduleEventListResponse(success=False, error=f"Failed to get upcoming events: {str(e)}")

    # レガシー互換性メソッド
    async def get_schedule_events(self, user_id: str, filters: dict[str, Any] | None = None) -> dict[str, Any]:
        """予定イベント一覧を取得（レガシー互換性）

        Args:
            user_id: ユーザーID
            filters: フィルター条件

        Returns:
            Dict[str, Any]: 取得結果
        """
        try:
            self.logger.info(f"予定イベント取得開始: user_id={user_id}")

            # フィルターからリクエストを構築
            request = SearchScheduleEventsRequest(
                user_id=user_id,
                status=filters.get("status") if filters else None,
                limit=50,
                offset=0,
            )

            response = await self.search_schedule_events(request)

            if response.success:
                return {"success": True, "data": response.schedule_events}
            else:
                return {"success": False, "message": response.error}

        except Exception as e:
            self.logger.error(f"予定イベント取得エラー: user_id={user_id}, error={e}")
            return {"success": False, "message": f"予定イベントの取得に失敗しました: {str(e)}"}

    async def get_schedule_event(self, user_id: str, event_id: str) -> dict[str, Any]:
        """特定の予定イベントを取得（レガシー互換性）

        Args:
            user_id: ユーザーID
            event_id: イベントID

        Returns:
            Dict[str, Any]: 取得結果
        """
        try:
            self.logger.info(f"予定イベント詳細取得開始: user_id={user_id}, event_id={event_id}")

            response = await self.get_schedule_event_new(event_id)

            if response.success:
                # ユーザー権限チェック
                if response.schedule_event.get("user_id") != user_id:
                    return {"success": False, "message": "アクセス権限がありません"}
                return {"success": True, "data": response.schedule_event}
            else:
                return {"success": False, "message": "予定が見つかりません"}

        except Exception as e:
            self.logger.error(f"予定イベント詳細取得エラー: user_id={user_id}, event_id={event_id}, error={e}")
            return {"success": False, "message": f"予定イベントの取得に失敗しました: {str(e)}"}

    async def update_schedule_event(self, user_id: str, event_id: str, update_data: dict) -> dict[str, Any]:
        """予定イベントを更新（レガシー互換性）

        Args:
            user_id: ユーザーID
            event_id: イベントID
            update_data: 更新データ

        Returns:
            Dict[str, Any]: 更新結果
        """
        try:
            self.logger.info(f"予定イベント更新開始: user_id={user_id}, event_id={event_id}")

            request = UpdateScheduleEventRequest(
                event_id=event_id,
                user_id=user_id,
                title=update_data.get("title"),
                date=update_data.get("date"),
                time=update_data.get("time"),
                event_type=update_data.get("type") or update_data.get("event_type"),
                location=update_data.get("location"),
                description=update_data.get("description"),
                status=update_data.get("status"),
            )

            response = await self.update_schedule_event_new(request)

            if response.success:
                return {"success": True, "data": response.schedule_event}
            else:
                return {"success": False, "message": response.error}

        except Exception as e:
            self.logger.error(f"予定イベント更新エラー: user_id={user_id}, event_id={event_id}, error={e}")
            return {"success": False, "message": f"予定イベントの更新に失敗しました: {str(e)}"}

    async def delete_schedule_event(self, user_id: str, event_id: str) -> dict[str, Any]:
        """予定イベントを削除（レガシー互換性）

        Args:
            user_id: ユーザーID
            event_id: イベントID

        Returns:
            Dict[str, Any]: 削除結果
        """
        try:
            self.logger.info(f"予定イベント削除開始: user_id={user_id}, event_id={event_id}")

            response = await self.delete_schedule_event_new(event_id, user_id)

            if response.success:
                return {"success": True, "message": "予定を削除しました"}
            else:
                return {"success": False, "message": response.error}

        except Exception as e:
            self.logger.error(f"予定イベント削除エラー: user_id={user_id}, event_id={event_id}, error={e}")
            return {"success": False, "message": f"予定イベントの削除に失敗しました: {str(e)}"}

    async def update_schedule_status(self, user_id: str, event_id: str, status: str) -> dict[str, Any]:
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

            request = UpdateScheduleEventRequest(
                event_id=event_id,
                user_id=user_id,
                status=status,
            )

            response = await self.update_schedule_event_new(request)

            if response.success:
                return {"success": True, "data": response.schedule_event}
            else:
                return {"success": False, "message": response.error}

        except Exception as e:
            self.logger.error(f"予定ステータス更新エラー: user_id={user_id}, event_id={event_id}, error={e}")
            return {"success": False, "message": f"予定ステータスの更新に失敗しました: {str(e)}"}
