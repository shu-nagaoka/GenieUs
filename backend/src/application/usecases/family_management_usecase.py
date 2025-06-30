"""家族情報管理UseCase

コーディング規約準拠:
- Import文ファイル先頭配置
- 型アノテーション完備
- DI注入パターン
- 段階的エラーハンドリング
"""

import logging
from dataclasses import dataclass
from typing import Any

from src.application.interface.protocols.family_repository import FamilyRepositoryProtocol
from src.domain.entities import FamilyInfo


@dataclass
class RegisterFamilyInfoRequest:
    """家族情報登録リクエスト"""

    user_id: str
    parent_name: str
    family_structure: str | None = None
    concerns: str | None = None
    living_area: str | None = None
    children: list[dict] | None = None


@dataclass
class UpdateFamilyInfoRequest:
    """家族情報更新リクエスト"""

    user_id: str
    parent_name: str | None = None
    family_structure: str | None = None
    concerns: str | None = None
    living_area: str | None = None
    children: list[dict] | None = None


@dataclass
class FamilyInfoResponse:
    """家族情報レスポンス"""

    success: bool
    family_info: dict[str, Any] | None = None
    error: str | None = None


class FamilyManagementUseCase:
    """家族情報管理UseCase

    責務:
    - 家族情報のCRUD操作
    - ユーザー別の家族情報管理
    - データ整合性の確保
    """

    def __init__(
        self,
        family_repository: FamilyRepositoryProtocol,
        logger: logging.Logger,
    ):
        """FamilyManagementUseCase初期化

        Args:
            family_repository: 家族情報リポジトリ
            logger: DIコンテナから注入されるロガー
        """
        self.family_repository = family_repository
        self.logger = logger

    async def register_family_info(self, user_id: str, family_data: dict) -> dict:
        """家族情報を登録

        Args:
            user_id: ユーザーID
            family_data: 家族情報データ

        Returns:
            Dict[str, Any]: 登録結果

        """
        try:
            self.logger.info(f"家族情報登録開始: user_id={user_id}")

            # 家族情報エンティティ作成
            family_info = FamilyInfo.from_dict(user_id, family_data)

            # 新しいSQLiteリポジトリに保存
            created_family = await self.family_repository.create(family_info)

            self.logger.info(f"家族情報登録完了: user_id={user_id}")
            return {"success": True, "message": "家族情報を登録しました", "family_id": created_family.family_id}

        except Exception as e:
            self.logger.error(f"家族情報登録エラー: user_id={user_id}, error={e}")
            return {"success": False, "error": f"家族情報の登録に失敗しました: {e!s}"}

    async def get_family_info(self, user_id: str) -> dict | None:
        """家族情報を取得

        Args:
            user_id: ユーザーID

        Returns:
            Optional[dict]: 家族情報、存在しない場合はNone

        """
        try:
            self.logger.info(f"家族情報取得開始: user_id={user_id}")

            # SQLiteリポジトリから取得
            family_info = await self.family_repository.get_by_user_id(user_id)

            if family_info:
                self.logger.info(f"家族情報取得成功: user_id={user_id}")
                return family_info.to_dict()
            else:
                self.logger.info(f"家族情報が見つかりません: user_id={user_id}")
                return None

        except Exception as e:
            self.logger.error(f"家族情報取得エラー: user_id={user_id}, error={e}")
            return None

    async def update_family_info(self, user_id: str, family_data: dict) -> dict:
        """家族情報を更新

        Args:
            user_id: ユーザーID
            family_data: 更新する家族情報データ

        Returns:
            Dict[str, Any]: 更新結果

        """
        try:
            self.logger.info(f"家族情報更新開始: user_id={user_id}")

            # 既存の家族情報を取得
            existing_family = await self.family_repository.get_by_user_id(user_id)
            if not existing_family:
                return {"success": False, "error": "更新対象の家族情報が見つかりません"}

            # 家族情報エンティティ更新
            updated_family = FamilyInfo.from_dict(user_id, family_data)
            updated_family.family_id = existing_family.family_id
            updated_family.created_at = existing_family.created_at  # 作成日時は保持

            # SQLiteリポジトリで更新
            await self.family_repository.update(updated_family)

            self.logger.info(f"家族情報更新完了: user_id={user_id}")
            return {"success": True, "message": "家族情報を更新しました"}

        except Exception as e:
            self.logger.error(f"家族情報更新エラー: user_id={user_id}, error={e}")
            return {"success": False, "error": f"家族情報の更新に失敗しました: {e!s}"}

    async def delete_family_info(self, user_id: str) -> dict:
        """家族情報を削除

        Args:
            user_id: ユーザーID

        Returns:
            Dict[str, Any]: 削除結果

        """
        try:
            self.logger.info(f"家族情報削除開始: user_id={user_id}")

            # SQLiteリポジトリで削除実行
            deleted = await self.family_repository.delete_by_user_id(user_id)

            if deleted:
                self.logger.info(f"家族情報削除完了: user_id={user_id}")
                return {"success": True, "message": "家族情報を削除しました"}
            else:
                self.logger.info(f"削除対象の家族情報が見つかりません: user_id={user_id}")
                return {"success": False, "message": "削除対象の家族情報が見つかりません"}

        except Exception as e:
            self.logger.error(f"家族情報削除エラー: user_id={user_id}, error={e}")
            return {"success": False, "error": f"家族情報の削除に失敗しました: {e!s}"}
