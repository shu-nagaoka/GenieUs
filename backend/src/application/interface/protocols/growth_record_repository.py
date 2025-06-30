"""成長記録リポジトリプロトコル

コーディング規約準拠:
- Import文ファイル先頭配置
- 型アノテーション完備
- プロトコル定義パターン
"""

from typing import Protocol
from src.domain.entities import GrowthRecord


class GrowthRecordRepositoryProtocol(Protocol):
    """成長記録リポジトリプロトコル"""

    def save_growth_record(self, growth_record: GrowthRecord) -> bool:
        """成長記録保存"""
        ...

    def get_growth_records(self, user_id: str) -> list[GrowthRecord]:
        """成長記録一覧取得"""
        ...

    def get_growth_record_by_id(self, record_id: str) -> GrowthRecord | None:
        """成長記録個別取得"""
        ...

    def delete_growth_record(self, record_id: str) -> bool:
        """成長記録削除"""
        ...
