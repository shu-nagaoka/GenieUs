"""メモリー記録管理UseCase"""

import logging
from typing import Dict, Any, List, Optional

from src.domain.entities import MemoryRecord


class MemoryRecordUseCase:
    """メモリー記録管理のビジネスロジック"""

    def __init__(self, memory_record_repository, logger: logging.Logger):
        """
        Args:
            memory_record_repository: メモリー記録リポジトリ
            logger: ロガー（DIコンテナから注入）
        """
        self.memory_record_repository = memory_record_repository
        self.logger = logger

    async def create_memory_record(self, user_id: str, record_data: dict) -> Dict[str, Any]:
        """メモリー記録を作成

        Args:
            user_id: ユーザーID
            record_data: メモリー記録データ

        Returns:
            Dict[str, Any]: 作成結果
        """
        try:
            self.logger.info(f"メモリー記録作成開始: user_id={user_id}")

            # メモリー記録エンティティ作成
            memory_record = MemoryRecord.from_dict(user_id, record_data)

            # リポジトリに保存
            result = await self.memory_record_repository.save_memory_record(memory_record)

            self.logger.info(f"メモリー記録作成完了: user_id={user_id}, memory_id={result.get('memory_id')}")
            return {"success": True, "id": result.get("memory_id"), "data": memory_record.to_dict()}

        except Exception as e:
            self.logger.error(f"メモリー記録作成エラー: user_id={user_id}, error={e}")
            return {"success": False, "message": f"メモリー記録の作成に失敗しました: {str(e)}"}

    async def get_memory_records(self, user_id: str, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """メモリー記録一覧を取得

        Args:
            user_id: ユーザーID
            filters: フィルター条件

        Returns:
            Dict[str, Any]: 取得結果
        """
        try:
            self.logger.info(f"メモリー記録取得開始: user_id={user_id}")

            # フィルター条件を処理
            processed_filters = {}
            if filters:
                if filters.get("type"):
                    processed_filters["type"] = filters["type"]
                if filters.get("category"):
                    processed_filters["category"] = filters["category"]
                if filters.get("favorited") is not None:
                    processed_filters["favorited"] = filters["favorited"]
                if filters.get("tags"):
                    # タグ文字列をリストに変換
                    if isinstance(filters["tags"], str):
                        processed_filters["tags"] = [tag.strip() for tag in filters["tags"].split(",")]
                    else:
                        processed_filters["tags"] = filters["tags"]

            records = await self.memory_record_repository.get_memory_records(user_id, processed_filters)

            self.logger.info(f"メモリー記録取得完了: user_id={user_id}, count={len(records)}")
            return {"success": True, "data": [record.to_dict() for record in records]}

        except Exception as e:
            self.logger.error(f"メモリー記録取得エラー: user_id={user_id}, error={e}")
            return {"success": False, "message": f"メモリー記録の取得に失敗しました: {str(e)}"}

    async def get_memory_record(self, user_id: str, memory_id: str) -> Dict[str, Any]:
        """特定のメモリー記録を取得

        Args:
            user_id: ユーザーID
            memory_id: メモリーID

        Returns:
            Dict[str, Any]: 取得結果
        """
        try:
            self.logger.info(f"メモリー記録詳細取得開始: user_id={user_id}, memory_id={memory_id}")

            record = await self.memory_record_repository.get_memory_record(user_id, memory_id)

            if record:
                self.logger.info(f"メモリー記録詳細取得成功: user_id={user_id}, memory_id={memory_id}")
                return {"success": True, "data": record.to_dict()}
            else:
                return {"success": False, "message": "メモリー記録が見つかりません"}

        except Exception as e:
            self.logger.error(f"メモリー記録詳細取得エラー: user_id={user_id}, memory_id={memory_id}, error={e}")
            return {"success": False, "message": f"メモリー記録の取得に失敗しました: {str(e)}"}

    async def update_memory_record(self, user_id: str, memory_id: str, update_data: dict) -> Dict[str, Any]:
        """メモリー記録を更新

        Args:
            user_id: ユーザーID
            memory_id: メモリーID
            update_data: 更新データ

        Returns:
            Dict[str, Any]: 更新結果
        """
        try:
            self.logger.info(f"メモリー記録更新開始: user_id={user_id}, memory_id={memory_id}")

            # 既存記録を取得
            existing_record = await self.memory_record_repository.get_memory_record(user_id, memory_id)
            if not existing_record:
                return {"success": False, "message": "メモリー記録が見つかりません"}

            # 更新データをマージ
            updated_data = existing_record.to_dict()
            updated_data.update(update_data)

            # エンティティ作成して保存
            updated_record = MemoryRecord.from_dict(user_id, updated_data)
            result = await self.memory_record_repository.update_memory_record(updated_record)

            self.logger.info(f"メモリー記録更新完了: user_id={user_id}, memory_id={memory_id}")
            return {"success": True, "data": updated_record.to_dict()}

        except Exception as e:
            self.logger.error(f"メモリー記録更新エラー: user_id={user_id}, memory_id={memory_id}, error={e}")
            return {"success": False, "message": f"メモリー記録の更新に失敗しました: {str(e)}"}

    async def delete_memory_record(self, user_id: str, memory_id: str) -> Dict[str, Any]:
        """メモリー記録を削除

        Args:
            user_id: ユーザーID
            memory_id: メモリーID

        Returns:
            Dict[str, Any]: 削除結果
        """
        try:
            self.logger.info(f"メモリー記録削除開始: user_id={user_id}, memory_id={memory_id}")

            result = await self.memory_record_repository.delete_memory_record(user_id, memory_id)

            if result:
                self.logger.info(f"メモリー記録削除完了: user_id={user_id}, memory_id={memory_id}")
                return {"success": True, "message": "メモリー記録を削除しました", "deleted_data": result.to_dict()}
            else:
                return {"success": False, "message": "メモリー記録が見つかりません"}

        except Exception as e:
            self.logger.error(f"メモリー記録削除エラー: user_id={user_id}, memory_id={memory_id}, error={e}")
            return {"success": False, "message": f"メモリー記録の削除に失敗しました: {str(e)}"}

    async def toggle_memory_favorite(self, user_id: str, memory_id: str, favorited: bool) -> Dict[str, Any]:
        """メモリーのお気に入り状態を切り替え

        Args:
            user_id: ユーザーID
            memory_id: メモリーID
            favorited: お気に入り状態

        Returns:
            Dict[str, Any]: 更新結果
        """
        try:
            self.logger.info(f"お気に入り状態更新開始: user_id={user_id}, memory_id={memory_id}, favorited={favorited}")

            # 既存記録を取得
            existing_record = await self.memory_record_repository.get_memory_record(user_id, memory_id)
            if not existing_record:
                return {"success": False, "message": "メモリー記録が見つかりません"}

            # お気に入り状態を更新
            existing_record.favorited = favorited
            result = await self.memory_record_repository.update_memory_record(existing_record)

            self.logger.info(f"お気に入り状態更新完了: user_id={user_id}, memory_id={memory_id}")
            return {"success": True, "data": existing_record.to_dict()}

        except Exception as e:
            self.logger.error(f"お気に入り状態更新エラー: user_id={user_id}, memory_id={memory_id}, error={e}")
            return {"success": False, "message": f"お気に入り状態の更新に失敗しました: {str(e)}"}

    async def get_favorite_memories(self, user_id: str) -> Dict[str, Any]:
        """お気に入りメモリーを取得

        Args:
            user_id: ユーザーID

        Returns:
            Dict[str, Any]: 取得結果
        """
        try:
            self.logger.info(f"お気に入りメモリー取得開始: user_id={user_id}")

            filters = {"favorited": True}
            records = await self.memory_record_repository.get_memory_records(user_id, filters)

            self.logger.info(f"お気に入りメモリー取得完了: user_id={user_id}, count={len(records)}")
            return {"success": True, "data": [record.to_dict() for record in records]}

        except Exception as e:
            self.logger.error(f"お気に入りメモリー取得エラー: user_id={user_id}, error={e}")
            return {"success": False, "message": f"お気に入りメモリーの取得に失敗しました: {str(e)}"}

    async def get_albums(self, user_id: str) -> Dict[str, Any]:
        """アルバム一覧を取得

        Args:
            user_id: ユーザーID

        Returns:
            Dict[str, Any]: 取得結果
        """
        try:
            self.logger.info(f"アルバム一覧取得開始: user_id={user_id}")

            filters = {"type": "album"}
            records = await self.memory_record_repository.get_memory_records(user_id, filters)

            self.logger.info(f"アルバム一覧取得完了: user_id={user_id}, count={len(records)}")
            return {"success": True, "data": [record.to_dict() for record in records]}

        except Exception as e:
            self.logger.error(f"アルバム一覧取得エラー: user_id={user_id}, error={e}")
            return {"success": False, "message": f"アルバム一覧の取得に失敗しました: {str(e)}"}

    async def get_memory_tags(self, user_id: str) -> Dict[str, Any]:
        """使用中のタグ一覧を取得

        Args:
            user_id: ユーザーID

        Returns:
            Dict[str, Any]: 取得結果
        """
        try:
            self.logger.info(f"タグ一覧取得開始: user_id={user_id}")

            tags = await self.memory_record_repository.get_all_tags(user_id)

            self.logger.info(f"タグ一覧取得完了: user_id={user_id}, count={len(tags)}")
            return {"success": True, "data": tags}

        except Exception as e:
            self.logger.error(f"タグ一覧取得エラー: user_id={user_id}, error={e}")
            return {"success": False, "message": f"タグ一覧の取得に失敗しました: {str(e)}"}
