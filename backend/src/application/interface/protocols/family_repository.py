"""家族情報リポジトリプロトコル

コーディング規約準拠:
- Import文ファイル先頭配置
- 型アノテーション完備
- プロトコル定義パターン
"""

from typing import Protocol
from src.domain.entities import FamilyInfo


class FamilyRepositoryProtocol(Protocol):
    """家族情報リポジトリプロトコル"""

    async def get_family_info(self, user_id: str) -> FamilyInfo | None:
        """家族情報取得"""
        ...

    async def save_family_info(self, family_info: FamilyInfo) -> dict:
        """家族情報保存"""
        ...

    async def update_family_info(self, family_info: FamilyInfo) -> bool:
        """家族情報更新"""
        ...

    async def delete_family_info(self, user_id: str) -> bool:
        """家族情報削除"""
        ...
