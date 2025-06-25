"""予定イベントリポジトリ - JSON永続化"""

import json
import logging
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from uuid import uuid4
from datetime import datetime

from src.domain.entities import ScheduleEvent


class ScheduleEventRepository:
    """予定イベントJSON永続化リポジトリ"""

    def __init__(self, logger: logging.Logger, data_dir: str = "data"):
        """
        Args:
            logger: ロガー（DIコンテナから注入）
            data_dir: データディレクトリ
        """
        self.logger = logger
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.file_path = self.data_dir / "schedules.json"

    def _load_events(self) -> Dict[str, Any]:
        """予定イベントデータを読み込み"""
        if self.file_path.exists():
            with open(self.file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def _save_events(self, events: Dict[str, Any]) -> None:
        """予定イベントデータを保存"""
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(events, f, ensure_ascii=False, indent=2)

    async def save_schedule_event(self, schedule_event: ScheduleEvent) -> dict:
        """予定イベントを保存

        Args:
            schedule_event: 予定イベントエンティティ

        Returns:
            dict: 保存結果
        """
        try:
            events = self._load_events()

            # 新規イベントの場合はIDを生成
            if not schedule_event.event_id:
                schedule_event.event_id = str(uuid4())

            # 現在時刻をセット
            now = datetime.now().isoformat()
            schedule_event.created_at = schedule_event.created_at or now
            schedule_event.updated_at = now

            # JSON形式で保存
            events[schedule_event.event_id] = schedule_event.to_dict()
            self._save_events(events)

            self.logger.info(f"予定イベント保存完了: event_id={schedule_event.event_id}")
            return {"event_id": schedule_event.event_id, "status": "saved"}

        except Exception as e:
            self.logger.error(f"予定イベント保存エラー: {e}")
            raise

    async def get_schedule_events(self, user_id: str, filters: Optional[Dict[str, Any]] = None) -> List[ScheduleEvent]:
        """予定イベント一覧を取得

        Args:
            user_id: ユーザーID
            filters: フィルター条件

        Returns:
            List[ScheduleEvent]: 予定イベント一覧
        """
        try:
            events = self._load_events()
            user_events = []

            for event_data in events.values():
                if event_data.get("user_id") == user_id:
                    # フィルター適用
                    if filters:
                        if filters.get("status") and event_data.get("status") != filters["status"]:
                            continue

                    # エンティティに変換
                    schedule_event = ScheduleEvent(
                        event_id=event_data.get("id"),
                        user_id=event_data.get("user_id"),
                        title=event_data.get("title"),
                        date=event_data.get("date"),
                        time=event_data.get("time"),
                        type=event_data.get("type"),
                        location=event_data.get("location"),
                        description=event_data.get("description"),
                        status=event_data.get("status", "upcoming"),
                        created_by=event_data.get("created_by", "genie"),
                        created_at=event_data.get("created_at"),
                        updated_at=event_data.get("updated_at"),
                    )
                    user_events.append(schedule_event)

            # 日付でソート
            user_events.sort(key=lambda x: x.date or "")

            self.logger.info(f"予定イベント一覧取得完了: user_id={user_id}, count={len(user_events)}")
            return user_events

        except Exception as e:
            self.logger.error(f"予定イベント一覧取得エラー: {e}")
            return []

    async def get_schedule_event(self, user_id: str, event_id: str) -> Optional[ScheduleEvent]:
        """特定の予定イベントを取得

        Args:
            user_id: ユーザーID
            event_id: イベントID

        Returns:
            Optional[ScheduleEvent]: 予定イベント、存在しない場合はNone
        """
        try:
            events = self._load_events()

            if event_id not in events:
                self.logger.info(f"予定イベントが見つかりません: event_id={event_id}")
                return None

            event_data = events[event_id]

            if event_data.get("user_id") != user_id:
                self.logger.warning(f"アクセス権限なし: user_id={user_id}, event_id={event_id}")
                return None

            # エンティティに変換
            schedule_event = ScheduleEvent(
                event_id=event_data.get("id"),
                user_id=event_data.get("user_id"),
                title=event_data.get("title"),
                date=event_data.get("date"),
                time=event_data.get("time"),
                type=event_data.get("type"),
                location=event_data.get("location"),
                description=event_data.get("description"),
                status=event_data.get("status", "upcoming"),
                created_by=event_data.get("created_by", "genie"),
                created_at=event_data.get("created_at"),
                updated_at=event_data.get("updated_at"),
            )

            self.logger.info(f"予定イベント取得完了: event_id={event_id}")
            return schedule_event

        except Exception as e:
            self.logger.error(f"予定イベント取得エラー: {e}")
            return None

    async def update_schedule_event(self, schedule_event: ScheduleEvent) -> dict:
        """予定イベントを更新

        Args:
            schedule_event: 更新する予定イベントエンティティ

        Returns:
            dict: 更新結果
        """
        try:
            events = self._load_events()

            if schedule_event.event_id not in events:
                raise ValueError(f"更新対象のイベントが見つかりません: {schedule_event.event_id}")

            # 更新時刻をセット
            schedule_event.updated_at = datetime.now().isoformat()

            # JSON形式で保存
            events[schedule_event.event_id] = schedule_event.to_dict()
            self._save_events(events)

            self.logger.info(f"予定イベント更新完了: event_id={schedule_event.event_id}")
            return {"event_id": schedule_event.event_id, "status": "updated"}

        except Exception as e:
            self.logger.error(f"予定イベント更新エラー: {e}")
            raise

    async def delete_schedule_event(self, user_id: str, event_id: str) -> Optional[ScheduleEvent]:
        """予定イベントを削除

        Args:
            user_id: ユーザーID
            event_id: イベントID

        Returns:
            Optional[ScheduleEvent]: 削除されたイベント、存在しない場合はNone
        """
        try:
            events = self._load_events()

            if event_id not in events:
                self.logger.info(f"削除対象の予定イベントが見つかりません: event_id={event_id}")
                return None

            event_data = events[event_id]

            if event_data.get("user_id") != user_id:
                self.logger.warning(f"削除権限なし: user_id={user_id}, event_id={event_id}")
                return None

            # エンティティに変換
            deleted_event = ScheduleEvent(
                event_id=event_data.get("id"),
                user_id=event_data.get("user_id"),
                title=event_data.get("title"),
                date=event_data.get("date"),
                time=event_data.get("time"),
                type=event_data.get("type"),
                location=event_data.get("location"),
                description=event_data.get("description"),
                status=event_data.get("status", "upcoming"),
                created_by=event_data.get("created_by", "genie"),
                created_at=event_data.get("created_at"),
                updated_at=event_data.get("updated_at"),
            )

            # ファイルから削除
            del events[event_id]
            self._save_events(events)

            self.logger.info(f"予定イベント削除完了: event_id={event_id}")
            return deleted_event

        except Exception as e:
            self.logger.error(f"予定イベント削除エラー: {e}")
            return None
