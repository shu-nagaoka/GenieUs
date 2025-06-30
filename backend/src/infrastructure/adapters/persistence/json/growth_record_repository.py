"""成長記録リポジトリ - JSON永続化"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from src.domain.entities import GrowthRecord


class GrowthRecordRepository:
    """成長記録JSON永続化リポジトリ"""

    def __init__(self, logger: logging.Logger, data_dir: str = "data"):
        """Args:
        logger: ロガー（DIコンテナから注入）
        data_dir: データディレクトリ

        """
        self.logger = logger
        self.data_dir = Path(data_dir)
        # Cloud Run用: データディレクトリ作成をオプション化（staging/productionともにスキップ）
        if os.getenv("ENVIRONMENT") not in ["production", "staging"]:
            self.data_dir.mkdir(exist_ok=True)
        self.file_path = self.data_dir / "growth_records.json"

    def _load_records(self) -> dict[str, Any]:
        """成長記録データを読み込み"""
        if self.file_path.exists():
            with open(self.file_path, encoding="utf-8") as f:
                return json.load(f)
        return {}

    def _save_records(self, records: dict[str, Any]) -> None:
        """成長記録データを保存"""
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(records, f, ensure_ascii=False, indent=2)

    async def save_growth_record(self, growth_record: GrowthRecord) -> dict:
        """成長記録を保存

        Args:
            growth_record: 成長記録エンティティ

        Returns:
            dict: 保存結果

        """
        try:
            records = self._load_records()

            # 新規記録の場合はIDを生成
            if not growth_record.record_id:
                growth_record.record_id = str(uuid4())

            # 現在時刻をセット
            now = datetime.now().isoformat()
            growth_record.created_at = growth_record.created_at or now
            growth_record.updated_at = now

            # JSON形式で保存
            records[growth_record.record_id] = growth_record.to_dict()
            self._save_records(records)

            self.logger.info(f"成長記録保存完了: record_id={growth_record.record_id}")
            return {"record_id": growth_record.record_id, "status": "saved"}

        except Exception as e:
            self.logger.error(f"成長記録保存エラー: {e}")
            raise

    async def get_growth_records(self, user_id: str, filters: dict[str, Any] | None = None) -> list[GrowthRecord]:
        """成長記録一覧を取得

        Args:
            user_id: ユーザーID
            filters: フィルター条件

        Returns:
            List[GrowthRecord]: 成長記録一覧

        """
        try:
            records = self._load_records()
            user_records = []

            for record_data in records.values():
                if record_data.get("user_id") == user_id:
                    # フィルター適用
                    if filters:
                        if filters.get("child_name") and record_data.get("child_name") != filters["child_name"]:
                            continue
                        if filters.get("type") and record_data.get("type") != filters["type"]:
                            continue
                        if filters.get("category") and record_data.get("category") != filters["category"]:
                            continue

                    # エンティティに変換
                    growth_record = GrowthRecord(
                        record_id=record_data.get("id"),
                        user_id=record_data.get("user_id"),
                        child_id=record_data.get("child_id"),
                        child_name=record_data.get("child_name"),
                        date=record_data.get("date"),
                        age_in_months=record_data.get("age_in_months", 0),
                        type=record_data.get("type"),
                        category=record_data.get("category"),
                        title=record_data.get("title"),
                        description=record_data.get("description"),
                        value=record_data.get("value"),
                        unit=record_data.get("unit"),
                        image_url=record_data.get("image_url"),
                        detected_by=record_data.get("detected_by", "parent"),
                        confidence=record_data.get("confidence"),
                        emotions=record_data.get("emotions"),
                        development_stage=record_data.get("development_stage"),
                        created_at=record_data.get("created_at"),
                        updated_at=record_data.get("updated_at"),
                    )
                    user_records.append(growth_record)

            # 日付でソート（新しい順）
            user_records.sort(key=lambda x: x.date or "", reverse=True)

            self.logger.info(f"成長記録一覧取得完了: user_id={user_id}, count={len(user_records)}")
            return user_records

        except Exception as e:
            self.logger.error(f"成長記録一覧取得エラー: {e}")
            return []

    async def get_growth_record(self, user_id: str, record_id: str) -> GrowthRecord | None:
        """特定の成長記録を取得

        Args:
            user_id: ユーザーID
            record_id: 記録ID

        Returns:
            Optional[GrowthRecord]: 成長記録、存在しない場合はNone

        """
        try:
            records = self._load_records()

            if record_id not in records:
                self.logger.info(f"成長記録が見つかりません: record_id={record_id}")
                return None

            record_data = records[record_id]

            if record_data.get("user_id") != user_id:
                self.logger.warning(f"アクセス権限なし: user_id={user_id}, record_id={record_id}")
                return None

            # エンティティに変換
            growth_record = GrowthRecord(
                record_id=record_data.get("id"),
                user_id=record_data.get("user_id"),
                child_id=record_data.get("child_id"),
                child_name=record_data.get("child_name"),
                date=record_data.get("date"),
                age_in_months=record_data.get("age_in_months", 0),
                type=record_data.get("type"),
                category=record_data.get("category"),
                title=record_data.get("title"),
                description=record_data.get("description"),
                value=record_data.get("value"),
                unit=record_data.get("unit"),
                image_url=record_data.get("image_url"),
                detected_by=record_data.get("detected_by", "parent"),
                confidence=record_data.get("confidence"),
                emotions=record_data.get("emotions"),
                development_stage=record_data.get("development_stage"),
                created_at=record_data.get("created_at"),
                updated_at=record_data.get("updated_at"),
            )

            self.logger.info(f"成長記録取得完了: record_id={record_id}")
            return growth_record

        except Exception as e:
            self.logger.error(f"成長記録取得エラー: {e}")
            return None

    async def update_growth_record(self, growth_record: GrowthRecord) -> dict:
        """成長記録を更新

        Args:
            growth_record: 更新する成長記録エンティティ

        Returns:
            dict: 更新結果

        """
        try:
            records = self._load_records()

            if growth_record.record_id not in records:
                raise ValueError(f"更新対象の記録が見つかりません: {growth_record.record_id}")

            # 更新時刻をセット
            growth_record.updated_at = datetime.now().isoformat()

            # JSON形式で保存
            records[growth_record.record_id] = growth_record.to_dict()
            self._save_records(records)

            self.logger.info(f"成長記録更新完了: record_id={growth_record.record_id}")
            return {"record_id": growth_record.record_id, "status": "updated"}

        except Exception as e:
            self.logger.error(f"成長記録更新エラー: {e}")
            raise

    async def delete_growth_record(self, user_id: str, record_id: str) -> GrowthRecord | None:
        """成長記録を削除

        Args:
            user_id: ユーザーID
            record_id: 記録ID

        Returns:
            Optional[GrowthRecord]: 削除された記録、存在しない場合はNone

        """
        try:
            records = self._load_records()

            if record_id not in records:
                self.logger.info(f"削除対象の成長記録が見つかりません: record_id={record_id}")
                return None

            record_data = records[record_id]

            if record_data.get("user_id") != user_id:
                self.logger.warning(f"削除権限なし: user_id={user_id}, record_id={record_id}")
                return None

            # エンティティに変換
            deleted_record = GrowthRecord(
                record_id=record_data.get("id"),
                user_id=record_data.get("user_id"),
                child_id=record_data.get("child_id"),
                child_name=record_data.get("child_name"),
                date=record_data.get("date"),
                age_in_months=record_data.get("age_in_months", 0),
                type=record_data.get("type"),
                category=record_data.get("category"),
                title=record_data.get("title"),
                description=record_data.get("description"),
                value=record_data.get("value"),
                unit=record_data.get("unit"),
                image_url=record_data.get("image_url"),
                detected_by=record_data.get("detected_by", "parent"),
                confidence=record_data.get("confidence"),
                emotions=record_data.get("emotions"),
                development_stage=record_data.get("development_stage"),
                created_at=record_data.get("created_at"),
                updated_at=record_data.get("updated_at"),
            )

            # ファイルから削除
            del records[record_id]
            self._save_records(records)

            self.logger.info(f"成長記録削除完了: record_id={record_id}")
            return deleted_record

        except Exception as e:
            self.logger.error(f"成長記録削除エラー: {e}")
            return None
