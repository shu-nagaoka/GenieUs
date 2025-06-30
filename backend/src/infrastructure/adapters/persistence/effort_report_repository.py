"""努力レポートリポジトリ - JSON永続化"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from src.application.interface.protocols.effort_report_repository import EffortReportRepositoryProtocol
from src.domain.entities import EffortReportRecord


class EffortReportRepository(EffortReportRepositoryProtocol):
    """努力レポートJSON永続化リポジトリ"""

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
        self.file_path = self.data_dir / "effort_reports.json"

    def _load_reports(self) -> dict[str, Any]:
        """努力レポートデータを読み込み"""
        if self.file_path.exists():
            with open(self.file_path, encoding="utf-8") as f:
                return json.load(f)
        return {}

    def _save_reports(self, reports: dict[str, Any]) -> None:
        """努力レポートデータを保存"""
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(reports, f, ensure_ascii=False, indent=2)

    async def save_effort_report(self, effort_report: EffortReportRecord) -> dict:
        """努力レポートを保存

        Args:
            effort_report: 努力レポートエンティティ

        Returns:
            dict: 保存結果

        """
        try:
            reports = self._load_reports()

            # 新規レポートの場合はIDを生成
            if not effort_report.report_id:
                effort_report.report_id = str(uuid4())

            # 現在時刻をセット
            now = datetime.now().isoformat()
            effort_report.created_at = effort_report.created_at or now
            effort_report.updated_at = now

            # JSON形式で保存
            reports[effort_report.report_id] = effort_report.to_dict()
            self._save_reports(reports)

            self.logger.info(f"努力レポート保存完了: report_id={effort_report.report_id}")
            return {"report_id": effort_report.report_id, "status": "saved"}

        except Exception as e:
            self.logger.error(f"努力レポート保存エラー: {e}")
            raise

    async def get_effort_reports(
        self,
        user_id: str,
        filters: dict[str, Any] | None = None,
    ) -> list[EffortReportRecord]:
        """努力レポート一覧を取得

        Args:
            user_id: ユーザーID
            filters: フィルター条件

        Returns:
            List[EffortReportRecord]: 努力レポート一覧

        """
        try:
            reports = self._load_reports()
            user_reports = []

            for report_data in reports.values():
                if report_data.get("user_id") == user_id:
                    # エンティティに変換
                    effort_report = EffortReportRecord(
                        report_id=report_data.get("id"),
                        user_id=report_data.get("user_id"),
                        period_days=report_data.get("period_days", 7),
                        effort_count=report_data.get("effort_count", 0),
                        score=report_data.get("score", 0.0),
                        highlights=report_data.get("highlights", []),
                        categories=report_data.get("categories", {}),
                        summary=report_data.get("summary", ""),
                        achievements=report_data.get("achievements", []),
                        created_at=report_data.get("created_at"),
                        updated_at=report_data.get("updated_at"),
                    )
                    user_reports.append(effort_report)

            # 作成日でソート（新しい順）
            user_reports.sort(key=lambda x: x.created_at or "", reverse=True)

            self.logger.info(f"努力レポート一覧取得完了: user_id={user_id}, count={len(user_reports)}")
            return user_reports

        except Exception as e:
            self.logger.error(f"努力レポート一覧取得エラー: {e}")
            return []

    async def get_effort_report(self, user_id: str, report_id: str) -> EffortReportRecord | None:
        """特定の努力レポートを取得

        Args:
            user_id: ユーザーID
            report_id: レポートID

        Returns:
            Optional[EffortReportRecord]: 努力レポート、存在しない場合はNone

        """
        try:
            reports = self._load_reports()

            if report_id not in reports:
                self.logger.info(f"努力レポートが見つかりません: report_id={report_id}")
                return None

            report_data = reports[report_id]

            if report_data.get("user_id") != user_id:
                self.logger.warning(f"アクセス権限なし: user_id={user_id}, report_id={report_id}")
                return None

            # エンティティに変換
            effort_report = EffortReportRecord(
                report_id=report_data.get("id"),
                user_id=report_data.get("user_id"),
                period_days=report_data.get("period_days", 7),
                effort_count=report_data.get("effort_count", 0),
                score=report_data.get("score", 0.0),
                highlights=report_data.get("highlights", []),
                categories=report_data.get("categories", {}),
                summary=report_data.get("summary", ""),
                achievements=report_data.get("achievements", []),
                created_at=report_data.get("created_at"),
                updated_at=report_data.get("updated_at"),
            )

            self.logger.info(f"努力レポート取得完了: report_id={report_id}")
            return effort_report

        except Exception as e:
            self.logger.error(f"努力レポート取得エラー: {e}")
            return None

    async def update_effort_report(self, effort_report: EffortReportRecord) -> dict:
        """努力レポートを更新

        Args:
            effort_report: 更新する努力レポートエンティティ

        Returns:
            dict: 更新結果

        """
        try:
            reports = self._load_reports()

            if effort_report.report_id not in reports:
                raise ValueError(f"更新対象のレポートが見つかりません: {effort_report.report_id}")

            # 更新時刻をセット
            effort_report.updated_at = datetime.now().isoformat()

            # JSON形式で保存
            reports[effort_report.report_id] = effort_report.to_dict()
            self._save_reports(reports)

            self.logger.info(f"努力レポート更新完了: report_id={effort_report.report_id}")
            return {"report_id": effort_report.report_id, "status": "updated"}

        except Exception as e:
            self.logger.error(f"努力レポート更新エラー: {e}")
            raise

    async def delete_effort_report(self, user_id: str, report_id: str) -> EffortReportRecord | None:
        """努力レポートを削除

        Args:
            user_id: ユーザーID
            report_id: レポートID

        Returns:
            Optional[EffortReportRecord]: 削除されたレポート、存在しない場合はNone

        """
        try:
            reports = self._load_reports()

            if report_id not in reports:
                self.logger.info(f"削除対象の努力レポートが見つかりません: report_id={report_id}")
                return None

            report_data = reports[report_id]

            if report_data.get("user_id") != user_id:
                self.logger.warning(f"削除権限なし: user_id={user_id}, report_id={report_id}")
                return None

            # エンティティに変換
            deleted_report = EffortReportRecord(
                report_id=report_data.get("id"),
                user_id=report_data.get("user_id"),
                period_days=report_data.get("period_days", 7),
                effort_count=report_data.get("effort_count", 0),
                score=report_data.get("score", 0.0),
                highlights=report_data.get("highlights", []),
                categories=report_data.get("categories", {}),
                summary=report_data.get("summary", ""),
                achievements=report_data.get("achievements", []),
                created_at=report_data.get("created_at"),
                updated_at=report_data.get("updated_at"),
            )

            # ファイルから削除
            del reports[report_id]
            self._save_reports(reports)

            self.logger.info(f"努力レポート削除完了: report_id={report_id}")
            return deleted_report

        except Exception as e:
            self.logger.error(f"努力レポート削除エラー: {e}")
            return None
