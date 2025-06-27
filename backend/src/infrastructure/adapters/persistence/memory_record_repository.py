"""メモリー記録リポジトリ - JSON永続化"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from src.domain.entities import MemoryRecord


class MemoryRecordRepository:
    """メモリー記録JSON永続化リポジトリ"""

    def __init__(self, logger: logging.Logger, data_dir: str = "data"):
        """Args:
        logger: ロガー（DIコンテナから注入）
        data_dir: データディレクトリ

        """
        self.logger = logger
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.file_path = self.data_dir / "memories.json"

    def _load_records(self) -> dict[str, Any]:
        """メモリー記録データを読み込み"""
        if self.file_path.exists():
            with open(self.file_path, encoding="utf-8") as f:
                return json.load(f)
        return {}

    def _save_records(self, records: dict[str, Any]) -> None:
        """メモリー記録データを保存"""
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(records, f, ensure_ascii=False, indent=2)

    async def save_memory_record(self, memory_record: MemoryRecord) -> dict:
        """メモリー記録を保存

        Args:
            memory_record: メモリー記録エンティティ

        Returns:
            dict: 保存結果

        """
        try:
            records = self._load_records()

            # 新規記録の場合はIDを生成
            if not memory_record.memory_id:
                memory_record.memory_id = str(uuid4())

            # 現在時刻をセット
            now = datetime.now().isoformat()
            memory_record.created_at = memory_record.created_at or now
            memory_record.updated_at = now

            # JSON形式で保存
            records[memory_record.memory_id] = memory_record.to_dict()
            self._save_records(records)

            self.logger.info(f"メモリー記録保存完了: memory_id={memory_record.memory_id}")
            return {"memory_id": memory_record.memory_id, "status": "saved"}

        except Exception as e:
            self.logger.error(f"メモリー記録保存エラー: {e}")
            raise

    async def get_memory_records(self, user_id: str, filters: dict[str, Any] | None = None) -> list[MemoryRecord]:
        """メモリー記録一覧を取得

        Args:
            user_id: ユーザーID
            filters: フィルター条件

        Returns:
            List[MemoryRecord]: メモリー記録一覧

        """
        try:
            records = self._load_records()
            user_records = []

            for record_data in records.values():
                if record_data.get("user_id") == user_id:
                    # フィルター適用
                    if filters:
                        if filters.get("type") and record_data.get("type") != filters["type"]:
                            continue
                        if filters.get("category") and record_data.get("category") != filters["category"]:
                            continue
                        if (
                            filters.get("favorited") is not None
                            and record_data.get("favorited") != filters["favorited"]
                        ):
                            continue
                        if filters.get("tags"):
                            tag_list = filters["tags"]
                            if not any(tag in record_data.get("tags", []) for tag in tag_list):
                                continue

                    # エンティティに変換
                    memory_record = MemoryRecord(
                        memory_id=record_data.get("id"),
                        user_id=record_data.get("user_id"),
                        title=record_data.get("title"),
                        description=record_data.get("description"),
                        date=record_data.get("date"),
                        type=record_data.get("type"),
                        category=record_data.get("category"),
                        media_url=record_data.get("media_url"),
                        thumbnail_url=record_data.get("thumbnail_url"),
                        location=record_data.get("location"),
                        tags=record_data.get("tags", []),
                        favorited=record_data.get("favorited", False),
                        created_at=record_data.get("created_at"),
                        updated_at=record_data.get("updated_at"),
                    )
                    user_records.append(memory_record)

            # 日付でソート（新しい順）
            user_records.sort(key=lambda x: x.date or "", reverse=True)

            self.logger.info(f"メモリー記録一覧取得完了: user_id={user_id}, count={len(user_records)}")
            return user_records

        except Exception as e:
            self.logger.error(f"メモリー記録一覧取得エラー: {e}")
            return []

    async def get_memory_record(self, user_id: str, memory_id: str) -> MemoryRecord | None:
        """特定のメモリー記録を取得

        Args:
            user_id: ユーザーID
            memory_id: メモリーID

        Returns:
            Optional[MemoryRecord]: メモリー記録、存在しない場合はNone

        """
        try:
            records = self._load_records()

            if memory_id not in records:
                self.logger.info(f"メモリー記録が見つかりません: memory_id={memory_id}")
                return None

            record_data = records[memory_id]

            if record_data.get("user_id") != user_id:
                self.logger.warning(f"アクセス権限なし: user_id={user_id}, memory_id={memory_id}")
                return None

            # エンティティに変換
            memory_record = MemoryRecord(
                memory_id=record_data.get("id"),
                user_id=record_data.get("user_id"),
                title=record_data.get("title"),
                description=record_data.get("description"),
                date=record_data.get("date"),
                type=record_data.get("type"),
                category=record_data.get("category"),
                media_url=record_data.get("media_url"),
                thumbnail_url=record_data.get("thumbnail_url"),
                location=record_data.get("location"),
                tags=record_data.get("tags", []),
                favorited=record_data.get("favorited", False),
                created_at=record_data.get("created_at"),
                updated_at=record_data.get("updated_at"),
            )

            self.logger.info(f"メモリー記録取得完了: memory_id={memory_id}")
            return memory_record

        except Exception as e:
            self.logger.error(f"メモリー記録取得エラー: {e}")
            return None

    async def update_memory_record(self, memory_record: MemoryRecord) -> dict:
        """メモリー記録を更新

        Args:
            memory_record: 更新するメモリー記録エンティティ

        Returns:
            dict: 更新結果

        """
        try:
            records = self._load_records()

            if memory_record.memory_id not in records:
                raise ValueError(f"更新対象の記録が見つかりません: {memory_record.memory_id}")

            # 更新時刻をセット
            memory_record.updated_at = datetime.now().isoformat()

            # JSON形式で保存
            records[memory_record.memory_id] = memory_record.to_dict()
            self._save_records(records)

            self.logger.info(f"メモリー記録更新完了: memory_id={memory_record.memory_id}")
            return {"memory_id": memory_record.memory_id, "status": "updated"}

        except Exception as e:
            self.logger.error(f"メモリー記録更新エラー: {e}")
            raise

    async def delete_memory_record(self, user_id: str, memory_id: str) -> MemoryRecord | None:
        """メモリー記録を削除

        Args:
            user_id: ユーザーID
            memory_id: メモリーID

        Returns:
            Optional[MemoryRecord]: 削除された記録、存在しない場合はNone

        """
        try:
            records = self._load_records()

            if memory_id not in records:
                self.logger.info(f"削除対象のメモリー記録が見つかりません: memory_id={memory_id}")
                return None

            record_data = records[memory_id]

            if record_data.get("user_id") != user_id:
                self.logger.warning(f"削除権限なし: user_id={user_id}, memory_id={memory_id}")
                return None

            # エンティティに変換
            deleted_record = MemoryRecord(
                memory_id=record_data.get("id"),
                user_id=record_data.get("user_id"),
                title=record_data.get("title"),
                description=record_data.get("description"),
                date=record_data.get("date"),
                type=record_data.get("type"),
                category=record_data.get("category"),
                media_url=record_data.get("media_url"),
                thumbnail_url=record_data.get("thumbnail_url"),
                location=record_data.get("location"),
                tags=record_data.get("tags", []),
                favorited=record_data.get("favorited", False),
                created_at=record_data.get("created_at"),
                updated_at=record_data.get("updated_at"),
            )

            # ファイルから削除
            del records[memory_id]
            self._save_records(records)

            self.logger.info(f"メモリー記録削除完了: memory_id={memory_id}")
            return deleted_record

        except Exception as e:
            self.logger.error(f"メモリー記録削除エラー: {e}")
            return None

    async def get_all_tags(self, user_id: str) -> list[str]:
        """ユーザーが使用中のタグ一覧を取得

        Args:
            user_id: ユーザーID

        Returns:
            List[str]: タグ一覧

        """
        try:
            records = self._load_records()
            user_records = [record for record in records.values() if record.get("user_id") == user_id]

            # 全タグを収集
            all_tags = []
            for record in user_records:
                all_tags.extend(record.get("tags", []))

            # 重複を削除してソート
            unique_tags = sorted(list(set(all_tags)))

            self.logger.info(f"タグ一覧取得完了: user_id={user_id}, count={len(unique_tags)}")
            return unique_tags

        except Exception as e:
            self.logger.error(f"タグ一覧取得エラー: {e}")
            return []
