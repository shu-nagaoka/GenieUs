"""メモリー記録リポジトリプロトコル

コーディング規約準拠:
- Import文ファイル先頭配置
- 型アノテーション完備
- プロトコル定義パターン
"""

from typing import Protocol
from src.domain.entities import MemoryRecord


class MemoryRecordRepositoryProtocol(Protocol):
    """メモリー記録リポジトリプロトコル"""

    def save_memory_record(self, memory_record: MemoryRecord) -> bool:
        """メモリー記録保存"""
        ...

    def get_memory_records(self, user_id: str) -> list[MemoryRecord]:
        """メモリー記録一覧取得"""
        ...

    def get_memory_record_by_id(self, record_id: str) -> MemoryRecord | None:
        """メモリー記録個別取得"""
        ...

    def delete_memory_record(self, record_id: str) -> bool:
        """メモリー記録削除"""
        ...
