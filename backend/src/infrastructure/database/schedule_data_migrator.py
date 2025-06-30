"""スケジュールデータマイグレーター

JSONファイルからSQLiteデータベースへのスケジュールデータ移行を実行
"""

import json
import logging
import os
from pathlib import Path
from typing import Any

from src.domain.entities import ScheduleEvent
from src.infrastructure.adapters.persistence.sqlite.schedule_record_repository_sqlite import ScheduleRecordRepository
from src.infrastructure.database.sqlite_manager import SQLiteManager


class ScheduleDataMigrator:
    """スケジュールデータマイグレーター

    責務:
    - JSONファイルからスケジュールデータを読み込み
    - SQLiteデータベースへのデータ移行
    - データ整合性の確保
    """

    def __init__(
        self,
        sqlite_manager: SQLiteManager,
        logger: logging.Logger,
        json_file_path: str = "data/schedules.json",
    ):
        """ScheduleDataMigrator初期化

        Args:
            sqlite_manager: SQLiteマネージャー
            logger: ロガー
            json_file_path: JSONファイルパス
        """
        self.sqlite_manager = sqlite_manager
        self.logger = logger
        self.json_file_path = Path(json_file_path)
        self.schedule_repository = ScheduleRecordRepository(sqlite_manager=sqlite_manager, logger=logger)

    async def migrate_schedule_data(self, force_overwrite: bool = False) -> dict[str, Any]:
        """スケジュールデータをJSONからSQLiteに移行

        Args:
            force_overwrite: 既存データの上書きを強制するか

        Returns:
            dict: 移行結果
        """
        try:
            self.logger.info("📅 スケジュールデータ移行開始")

            # テーブル初期化
            await self.schedule_repository.initialize_table()

            # JSONファイル存在チェック
            if not self.json_file_path.exists():
                self.logger.warning(f"JSONファイルが見つかりません: {self.json_file_path}")
                return {
                    "success": True,
                    "message": "JSONファイルが存在しないため、移行をスキップしました",
                    "migrated_count": 0,
                    "skipped_count": 0,
                    "error_count": 0,
                }

            # JSONデータ読み込み
            schedule_data = self._load_json_data()
            if not schedule_data:
                return {
                    "success": True,
                    "message": "移行対象のデータがありません",
                    "migrated_count": 0,
                    "skipped_count": 0,
                    "error_count": 0,
                }

            # データ移行実行
            result = await self._migrate_events(schedule_data, force_overwrite)

            self.logger.info(
                f"✅ スケジュールデータ移行完了: "
                f"移行={result['migrated_count']}, "
                f"スキップ={result['skipped_count']}, "
                f"エラー={result['error_count']}"
            )

            return result

        except Exception as e:
            self.logger.error(f"❌ スケジュールデータ移行エラー: {e}")
            return {
                "success": False,
                "message": f"移行に失敗しました: {str(e)}",
                "migrated_count": 0,
                "skipped_count": 0,
                "error_count": 0,
            }

    def _load_json_data(self) -> dict[str, Any]:
        """JSONファイルからデータを読み込み

        Returns:
            dict: スケジュールデータ
        """
        try:
            with open(self.json_file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.logger.info(f"JSONデータ読み込み完了: {len(data)}件")
                return data

        except Exception as e:
            self.logger.error(f"❌ JSONファイル読み込みエラー: {e}")
            return {}

    async def _migrate_events(self, schedule_data: dict[str, Any], force_overwrite: bool) -> dict[str, Any]:
        """イベントデータを移行

        Args:
            schedule_data: スケジュールデータ
            force_overwrite: 上書きフラグ

        Returns:
            dict: 移行結果
        """
        migrated_count = 0
        skipped_count = 0
        error_count = 0

        for event_id, event_data in schedule_data.items():
            try:
                # 既存データチェック
                if not force_overwrite:
                    existing_event = await self.schedule_repository.get_by_id(event_id)
                    if existing_event:
                        self.logger.debug(f"⏭️ スケジュールイベントスキップ（既存）: {event_id}")
                        skipped_count += 1
                        continue

                # ScheduleEventエンティティ作成
                schedule_event = self._convert_json_to_entity(event_data)

                # SQLiteに保存
                await self.schedule_repository.create(schedule_event)

                self.logger.debug(f"✅ スケジュールイベント移行完了: {event_id}")
                migrated_count += 1

            except Exception as e:
                self.logger.error(f"❌ スケジュールイベント移行エラー: {event_id}, {e}")
                error_count += 1

        return {
            "success": True,
            "message": f"移行完了: {migrated_count}件移行, {skipped_count}件スキップ, {error_count}件エラー",
            "migrated_count": migrated_count,
            "skipped_count": skipped_count,
            "error_count": error_count,
        }

    def _convert_json_to_entity(self, event_data: dict[str, Any]) -> ScheduleEvent:
        """JSONデータをScheduleEventエンティティに変換

        Args:
            event_data: JSONイベントデータ

        Returns:
            ScheduleEvent: スケジュールイベントエンティティ
        """
        try:
            # IDを正規化（event_idフィールドがない場合はidを使用）
            event_id = event_data.get("id") or event_data.get("event_id", "")

            schedule_event = ScheduleEvent(
                event_id=event_id,
                user_id=event_data.get("user_id", ""),
                title=event_data.get("title", ""),
                date=event_data.get("date", ""),
                time=event_data.get("time", ""),
                type=event_data.get("type", ""),
                location=event_data.get("location"),
                description=event_data.get("description"),
                status=event_data.get("status", "upcoming"),
                created_by=event_data.get("created_by", "genie"),
                created_at=event_data.get("created_at"),
                updated_at=event_data.get("updated_at"),
            )

            return schedule_event

        except Exception as e:
            self.logger.error(f"❌ JSONデータ変換エラー: {e}")
            raise ValueError(f"JSONデータをScheduleEventに変換できません: {str(e)}")

    async def backup_json_data(self, backup_suffix: str = "_backup") -> bool:
        """JSONファイルをバックアップ

        Args:
            backup_suffix: バックアップファイルのサフィックス

        Returns:
            bool: バックアップ成功フラグ
        """
        try:
            if not self.json_file_path.exists():
                self.logger.info("バックアップ対象のJSONファイルが存在しません")
                return True

            backup_path = self.json_file_path.parent / f"{self.json_file_path.stem}{backup_suffix}.json"

            # バックアップ作成
            import shutil

            shutil.copy2(self.json_file_path, backup_path)

            self.logger.info(f"📁 JSONファイルバックアップ完了: {backup_path}")
            return True

        except Exception as e:
            self.logger.error(f"❌ JSONファイルバックアップエラー: {e}")
            return False

    async def verify_migration(self) -> dict[str, Any]:
        """移行データの整合性確認

        Returns:
            dict: 確認結果
        """
        try:
            self.logger.info("🔍 移行データ整合性確認開始")

            # JSONデータ読み込み
            json_data = self._load_json_data()
            json_count = len(json_data)

            # SQLiteデータ件数確認
            sqlite_events = await self.schedule_repository.search(
                user_id="",  # 全ユーザー対象
                limit=10000,  # 大きな値で全件取得
            )
            sqlite_count = len(sqlite_events)

            self.logger.info(f"📊 データ件数比較: JSON={json_count}件, SQLite={sqlite_count}件")

            # 個別データ整合性確認
            match_count = 0
            mismatch_details = []

            for event_id, json_event in json_data.items():
                sqlite_event = await self.schedule_repository.get_by_id(event_id)

                if sqlite_event:
                    # 基本フィールド比較
                    if sqlite_event.title == json_event.get("title") and sqlite_event.user_id == json_event.get(
                        "user_id"
                    ):
                        match_count += 1
                    else:
                        mismatch_details.append({"event_id": event_id, "issue": "データ不一致"})
                else:
                    mismatch_details.append({"event_id": event_id, "issue": "SQLiteに存在しない"})

            success = json_count == sqlite_count and match_count == json_count

            result = {
                "success": success,
                "json_count": json_count,
                "sqlite_count": sqlite_count,
                "match_count": match_count,
                "mismatch_count": len(mismatch_details),
                "mismatch_details": mismatch_details[:10],  # 最初の10件のみ
            }

            if success:
                self.logger.info("✅ 移行データ整合性確認: 問題なし")
            else:
                self.logger.warning(f"⚠️ 移行データ整合性確認: {len(mismatch_details)}件の不整合")

            return result

        except Exception as e:
            self.logger.error(f"❌ 移行データ整合性確認エラー: {e}")
            return {
                "success": False,
                "error": str(e),
                "json_count": 0,
                "sqlite_count": 0,
                "match_count": 0,
                "mismatch_count": 0,
                "mismatch_details": [],
            }
