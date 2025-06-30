"""努力レポート管理UseCase"""

import logging
from typing import Any

from src.application.interface.protocols.effort_report_repository import EffortReportRepositoryProtocol
from src.domain.entities import EffortReportRecord


class EffortReportUseCase:
    """努力レポート管理のビジネスロジック"""

    def __init__(self, effort_report_repository: EffortReportRepositoryProtocol, logger: logging.Logger):
        """Args:
        effort_report_repository: 努力レポートリポジトリ
        logger: ロガー（DIコンテナから注入）

        """
        self.effort_report_repository = effort_report_repository
        self.logger = logger

    async def create_effort_report(self, user_id: str, report_data: dict) -> dict[str, Any]:
        """努力レポートを作成

        Args:
            user_id: ユーザーID
            report_data: 努力レポートデータ

        Returns:
            Dict[str, Any]: 作成結果

        """
        try:
            self.logger.info(f"努力レポート作成開始: user_id={user_id}")

            # 努力レポートエンティティ作成
            effort_report = EffortReportRecord.from_dict(user_id, report_data)

            # リポジトリに保存
            result = await self.effort_report_repository.save_effort_report(effort_report)

            self.logger.info(f"努力レポート作成完了: user_id={user_id}, report_id={result.get('report_id')}")
            return {"success": True, "id": result.get("report_id"), "data": effort_report.to_dict()}

        except Exception as e:
            self.logger.error(f"努力レポート作成エラー: user_id={user_id}, error={e}")
            return {"success": False, "message": f"努力レポートの作成に失敗しました: {e!s}"}

    async def get_effort_reports(self, user_id: str, filters: dict[str, Any] | None = None) -> dict[str, Any]:
        """努力レポート一覧を取得

        Args:
            user_id: ユーザーID
            filters: フィルター条件

        Returns:
            Dict[str, Any]: 取得結果

        """
        try:
            self.logger.info(f"努力レポート取得開始: user_id={user_id}")

            reports = await self.effort_report_repository.get_effort_reports(user_id, filters)

            self.logger.info(f"努力レポート取得完了: user_id={user_id}, count={len(reports)}")
            return {"success": True, "data": [report.to_dict() for report in reports]}

        except Exception as e:
            self.logger.error(f"努力レポート取得エラー: user_id={user_id}, error={e}")
            return {"success": False, "message": f"努力レポートの取得に失敗しました: {e!s}"}

    async def get_effort_report(self, user_id: str, report_id: str) -> dict[str, Any]:
        """特定の努力レポートを取得

        Args:
            user_id: ユーザーID
            report_id: レポートID

        Returns:
            Dict[str, Any]: 取得結果

        """
        try:
            self.logger.info(f"努力レポート詳細取得開始: user_id={user_id}, report_id={report_id}")

            report = await self.effort_report_repository.get_effort_report(user_id, report_id)

            if report:
                self.logger.info(f"努力レポート詳細取得成功: user_id={user_id}, report_id={report_id}")
                return {"success": True, "data": report.to_dict()}
            else:
                return {"success": False, "message": "努力レポートが見つかりません"}

        except Exception as e:
            self.logger.error(f"努力レポート詳細取得エラー: user_id={user_id}, report_id={report_id}, error={e}")
            return {"success": False, "message": f"努力レポートの取得に失敗しました: {e!s}"}

    async def update_effort_report(self, user_id: str, report_id: str, update_data: dict) -> dict[str, Any]:
        """努力レポートを更新

        Args:
            user_id: ユーザーID
            report_id: レポートID
            update_data: 更新データ

        Returns:
            Dict[str, Any]: 更新結果

        """
        try:
            self.logger.info(f"努力レポート更新開始: user_id={user_id}, report_id={report_id}")

            # 既存レポートを取得
            existing_report = await self.effort_report_repository.get_effort_report(user_id, report_id)
            if not existing_report:
                return {"success": False, "message": "努力レポートが見つかりません"}

            # 更新データをマージ
            updated_data = existing_report.to_dict()
            updated_data.update(update_data)

            # エンティティ作成して保存
            updated_report = EffortReportRecord.from_dict(user_id, updated_data)
            result = await self.effort_report_repository.update_effort_report(updated_report)

            self.logger.info(f"努力レポート更新完了: user_id={user_id}, report_id={report_id}")
            return {"success": True, "data": updated_report.to_dict()}

        except Exception as e:
            self.logger.error(f"努力レポート更新エラー: user_id={user_id}, report_id={report_id}, error={e}")
            return {"success": False, "message": f"努力レポートの更新に失敗しました: {e!s}"}

    async def delete_effort_report(self, user_id: str, report_id: str) -> dict[str, Any]:
        """努力レポートを削除

        Args:
            user_id: ユーザーID
            report_id: レポートID

        Returns:
            Dict[str, Any]: 削除結果

        """
        try:
            self.logger.info(f"努力レポート削除開始: user_id={user_id}, report_id={report_id}")

            result = await self.effort_report_repository.delete_effort_report(user_id, report_id)

            if result:
                self.logger.info(f"努力レポート削除完了: user_id={user_id}, report_id={report_id}")
                return {"success": True, "message": "努力レポートを削除しました", "deleted_data": result.to_dict()}
            else:
                return {"success": False, "message": "努力レポートが見つかりません"}

        except Exception as e:
            self.logger.error(f"努力レポート削除エラー: user_id={user_id}, report_id={report_id}, error={e}")
            return {"success": False, "message": f"努力レポートの削除に失敗しました: {e!s}"}

    async def generate_effort_report(self, user_id: str, period_days: int = 7) -> dict[str, Any]:
        """努力レポートを自動生成

        Args:
            user_id: ユーザーID
            period_days: 期間（日数）

        Returns:
            Dict[str, Any]: 生成結果

        """
        try:
            self.logger.info(f"努力レポート自動生成開始: user_id={user_id}, period_days={period_days}")

            # サンプルデータで自動生成（実際は他のデータソースから分析）
            generated_data = {
                "period_days": period_days,
                "effort_count": 15,
                "score": 85.5,
                "highlights": [
                    "今週は毎日の記録を欠かさず継続できました",
                    "子どもの成長記録が前週比で3件増加しました",
                    "新しい遊びを2つ試してみました",
                ],
                "categories": {"記録継続": 7, "新しい取り組み": 2, "子どもとの時間": 6},
                "summary": f"過去{period_days}日間で素晴らしい子育ての記録を残されました。特に継続的な記録が印象的です。",
                "achievements": ["7日連続記録達成", "成長記録3件追加", "新しい遊び開拓"],
            }

            # エンティティ作成
            effort_report = EffortReportRecord.from_dict(user_id, generated_data)

            # リポジトリに保存
            result = await self.effort_report_repository.save_effort_report(effort_report)

            self.logger.info(f"努力レポート自動生成完了: user_id={user_id}, report_id={result.get('report_id')}")
            return {"success": True, "id": result.get("report_id"), "data": effort_report.to_dict()}

        except Exception as e:
            self.logger.error(f"努力レポート自動生成エラー: user_id={user_id}, error={e}")
            return {"success": False, "message": f"努力レポートの自動生成に失敗しました: {e!s}"}
