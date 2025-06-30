"""努力レポートリポジトリプロトコル

コーディング規約準拠:
- Import文ファイル先頭配置
- 型アノテーション完備
- プロトコル定義パターン
"""

from typing import Protocol
from src.domain.entities import EffortReportRecord


class EffortReportRepositoryProtocol(Protocol):
    """努力レポートリポジトリプロトコル"""

    def save_effort_report(self, effort_report: EffortReportRecord) -> bool:
        """努力レポート保存"""
        ...

    def get_effort_reports(self, user_id: str) -> list[EffortReportRecord]:
        """努力レポート一覧取得"""
        ...

    def get_effort_report_by_id(self, report_id: str) -> EffortReportRecord | None:
        """努力レポート個別取得"""
        ...

    def delete_effort_report(self, report_id: str) -> bool:
        """努力レポート削除"""
        ...
