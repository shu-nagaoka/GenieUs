"""家族情報リポジトリ - JSON永続化"""

import json
import logging
import os
from pathlib import Path

from src.domain.entities import FamilyInfo


class FamilyRepository:
    """家族情報JSON永続化リポジトリ"""

    def __init__(self, logger: logging.Logger, data_dir: str = "data"):
        """Args:
        logger: ロガー（DIコンテナから注入）
        data_dir: データディレクトリ

        """
        self.logger = logger
        self.data_dir = Path(data_dir)
        # Cloud Run用: データディレクトリ作成をオプション化
        if os.getenv("ENVIRONMENT") != "production":
            self.data_dir.mkdir(exist_ok=True)

    async def save_family_info(self, family_info: FamilyInfo) -> dict:
        """家族情報を保存

        Args:
            family_info: 家族情報エンティティ

        Returns:
            dict: 保存結果

        """
        try:
            # 本番環境ではファイル保存をスキップ（データディレクトリなし）
            if os.getenv("ENVIRONMENT") == "production":
                self.logger.info(f"本番環境: 家族情報保存をスキップ - {family_info.user_id}")
                return {"family_id": family_info.family_id, "status": "skipped_production"}
            
            file_path = self.data_dir / f"{family_info.user_id}_family.json"

            # JSONファイルに保存
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(family_info.to_dict(), f, ensure_ascii=False, indent=2)

            self.logger.info(f"家族情報保存完了: {file_path}")
            return {"family_id": family_info.family_id, "status": "saved"}

        except Exception as e:
            self.logger.error(f"家族情報保存エラー: {e}")
            raise

    async def get_family_info(self, user_id: str) -> FamilyInfo | None:
        """家族情報を取得

        Args:
            user_id: ユーザーID

        Returns:
            Optional[FamilyInfo]: 家族情報、存在しない場合はNone

        """
        try:
            # 本番環境ではファイル読み込みをスキップ（データディレクトリなし）
            if os.getenv("ENVIRONMENT") == "production":
                self.logger.info(f"本番環境: 家族情報取得をスキップ - {user_id}")
                return None
            
            file_path = self.data_dir / f"{user_id}_family.json"

            if not file_path.exists():
                self.logger.info(f"家族情報ファイルが見つかりません: {file_path}")
                return None

            # JSONファイルから読み込み
            with open(file_path, encoding="utf-8") as f:
                family_data = json.load(f)

            # FamilyInfoエンティティに変換
            family_info = FamilyInfo(
                family_id=family_data.get("family_id", ""),
                user_id=family_data.get("user_id", ""),
                parent_name=family_data.get("parent_name", ""),
                family_structure=family_data.get("family_structure", ""),
                concerns=family_data.get("concerns", ""),
                living_area=family_data.get("living_area", ""),
                children=family_data.get("children", []),
            )

            self.logger.info(f"家族情報取得完了: {file_path}")
            return family_info

        except Exception as e:
            self.logger.error(f"家族情報取得エラー: {e}")
            return None

    async def delete_family_info(self, user_id: str) -> bool:
        """家族情報を削除

        Args:
            user_id: ユーザーID

        Returns:
            bool: 削除成功したかどうか

        """
        try:
            # 本番環境ではファイル削除をスキップ（データディレクトリなし）
            if os.getenv("ENVIRONMENT") == "production":
                self.logger.info(f"本番環境: 家族情報削除をスキップ - {user_id}")
                return True
            
            file_path = self.data_dir / f"{user_id}_family.json"

            if file_path.exists():
                os.remove(file_path)
                self.logger.info(f"家族情報削除完了: {file_path}")
                return True
            else:
                self.logger.info(f"削除対象の家族情報が見つかりません: {file_path}")
                return False

        except Exception as e:
            self.logger.error(f"家族情報削除エラー: {e}")
            return False
