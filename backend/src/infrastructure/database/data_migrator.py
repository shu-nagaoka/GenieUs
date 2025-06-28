"""データ移行ツール - JSONファイル → SQLite"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from src.config.settings import AppSettings
from src.infrastructure.database.sqlite_manager import SQLiteManager


class DataMigrator:
    """既存JSONデータのSQLite移行管理"""

    def __init__(self, settings: AppSettings, sqlite_manager: SQLiteManager, logger: logging.Logger):
        self.settings = settings
        self.sqlite_manager = sqlite_manager
        self.logger = logger
        self.data_dir = Path(settings.ROOT_DIR) / "data"

    async def migrate_all_data(self) -> dict[str, Any]:
        """全データの移行実行"""
        self.logger.info("データ移行開始")
        migration_results = {
            "success": True,
            "migrated_files": [],
            "errors": [],
            "summary": {},
        }

        try:
            # 1. family情報の移行
            family_results = await self._migrate_family_data()
            migration_results["summary"]["family"] = family_results

            # 2. growth_records の移行
            growth_results = await self._migrate_growth_records()
            migration_results["summary"]["growth_records"] = growth_results

            # 3. effort_reports の移行
            effort_results = await self._migrate_effort_reports()
            migration_results["summary"]["effort_reports"] = effort_results

            # 4. 他のエンティティも同様に追加可能

            self.logger.info(
                "データ移行完了",
                extra={
                    "total_migrated": sum(r.get("migrated_count", 0) for r in migration_results["summary"].values()),
                },
            )

            return migration_results

        except Exception as e:
            self.logger.error(f"データ移行エラー: {e}")
            migration_results["success"] = False
            migration_results["errors"].append(str(e))
            return migration_results

    async def _migrate_family_data(self) -> dict[str, Any]:
        """家族情報データの移行"""
        self.logger.info("家族情報データ移行開始")
        result = {"migrated_count": 0, "errors": []}

        try:
            # JSONファイルパターンをスキャン: *_family.json
            family_files = list(self.data_dir.glob("*_family.json"))

            for family_file in family_files:
                try:
                    # ファイル名からuser_idを抽出 (例: frontend_user_family.json → frontend_user)
                    user_id = family_file.stem.replace("_family", "")

                    # JSONファイル読み込み
                    with open(family_file, encoding="utf-8") as f:
                        family_data = json.load(f)

                    # SQLiteに挿入
                    await self._insert_family_data(user_id, family_data)
                    result["migrated_count"] += 1

                    self.logger.debug(f"家族情報移行完了: {family_file.name}")

                except Exception as e:
                    error_msg = f"家族情報移行エラー ({family_file.name}): {e}"
                    self.logger.warning(error_msg)
                    result["errors"].append(error_msg)

            self.logger.info(f"家族情報データ移行完了: {result['migrated_count']}件")
            return result

        except Exception as e:
            self.logger.error(f"家族情報データ移行エラー: {e}")
            result["errors"].append(str(e))
            return result

    async def _insert_family_data(self, user_id: str, family_data: dict[str, Any]) -> None:
        """家族情報をSQLiteに挿入"""
        # デフォルトユーザー作成（必要に応じて）
        await self._ensure_default_user(user_id)

        # SQLite形式に変換
        family_id = family_data.get("family_id", f"{user_id}_family")

        query = """
        INSERT OR REPLACE INTO family_info (
            family_id, user_id, parent_name, family_structure, 
            concerns, living_area, children, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        params = (
            family_id,
            user_id,
            family_data.get("parent_name", ""),
            family_data.get("family_structure", ""),
            family_data.get("concerns", ""),
            family_data.get("living_area", ""),
            json.dumps(family_data.get("children", []), ensure_ascii=False),
            family_data.get("created_at", datetime.now().isoformat()),
            family_data.get("updated_at", datetime.now().isoformat()),
        )

        self.sqlite_manager.execute_update(query, params)

    async def _migrate_growth_records(self) -> dict[str, Any]:
        """成長記録データの移行"""
        self.logger.info("成長記録データ移行開始")
        result = {"migrated_count": 0, "errors": []}

        try:
            growth_file = self.data_dir / "growth_records.json"

            if growth_file.exists():
                with open(growth_file, encoding="utf-8") as f:
                    growth_data = json.load(f)

                # リスト形式の場合
                if isinstance(growth_data, list):
                    for record in growth_data:
                        try:
                            await self._insert_growth_record(record)
                            result["migrated_count"] += 1
                        except Exception as e:
                            error_msg = f"成長記録移行エラー: {e}"
                            result["errors"].append(error_msg)

                # 辞書形式の場合（ユーザーID別）
                elif isinstance(growth_data, dict):
                    for user_id, records in growth_data.items():
                        if isinstance(records, list):
                            for record in records:
                                try:
                                    record["user_id"] = user_id  # user_idを補完
                                    await self._insert_growth_record(record)
                                    result["migrated_count"] += 1
                                except Exception as e:
                                    error_msg = f"成長記録移行エラー ({user_id}): {e}"
                                    result["errors"].append(error_msg)

            self.logger.info(f"成長記録データ移行完了: {result['migrated_count']}件")
            return result

        except Exception as e:
            self.logger.error(f"成長記録データ移行エラー: {e}")
            result["errors"].append(str(e))
            return result

    async def _insert_growth_record(self, record_data: dict[str, Any]) -> None:
        """成長記録をSQLiteに挿入"""
        user_id = record_data.get("user_id", "frontend_user")
        await self._ensure_default_user(user_id)

        query = """
        INSERT OR REPLACE INTO growth_records (
            id, user_id, child_id, record_date, height_cm, weight_kg,
            head_circumference_cm, chest_circumference_cm, milestone_description,
            notes, photo_paths, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        params = (
            record_data.get("id", f"{user_id}_{datetime.now().isoformat()}"),
            user_id,
            record_data.get("child_id", ""),
            record_data.get("record_date", datetime.now().date().isoformat()),
            record_data.get("height_cm"),
            record_data.get("weight_kg"),
            record_data.get("head_circumference_cm"),
            record_data.get("chest_circumference_cm"),
            record_data.get("milestone_description", ""),
            record_data.get("notes", ""),
            json.dumps(record_data.get("photo_paths", []), ensure_ascii=False),
            record_data.get("created_at", datetime.now().isoformat()),
            record_data.get("updated_at", datetime.now().isoformat()),
        )

        self.sqlite_manager.execute_update(query, params)

    async def _migrate_effort_reports(self) -> dict[str, Any]:
        """努力レポートデータの移行"""
        self.logger.info("努力レポートデータ移行開始")
        result = {"migrated_count": 0, "errors": []}

        try:
            effort_file = self.data_dir / "effort_reports.json"

            if effort_file.exists():
                with open(effort_file, encoding="utf-8") as f:
                    effort_data = json.load(f)

                # データ構造に応じて処理
                if isinstance(effort_data, list):
                    for report in effort_data:
                        try:
                            await self._insert_effort_report(report)
                            result["migrated_count"] += 1
                        except Exception as e:
                            error_msg = f"努力レポート移行エラー: {e}"
                            result["errors"].append(error_msg)

                elif isinstance(effort_data, dict):
                    for user_id, reports in effort_data.items():
                        if isinstance(reports, list):
                            for report in reports:
                                try:
                                    report["user_id"] = user_id
                                    await self._insert_effort_report(report)
                                    result["migrated_count"] += 1
                                except Exception as e:
                                    error_msg = f"努力レポート移行エラー ({user_id}): {e}"
                                    result["errors"].append(error_msg)

            self.logger.info(f"努力レポートデータ移行完了: {result['migrated_count']}件")
            return result

        except Exception as e:
            self.logger.error(f"努力レポートデータ移行エラー: {e}")
            result["errors"].append(str(e))
            return result

    async def _insert_effort_report(self, report_data: dict[str, Any]) -> None:
        """努力レポートをSQLiteに挿入"""
        user_id = report_data.get("user_id", "frontend_user")
        await self._ensure_default_user(user_id)

        query = """
        INSERT OR REPLACE INTO effort_reports (
            id, user_id, date, daily_effort_summary, challenges,
            achievements, reflection, goals_for_tomorrow, mood_score,
            created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        params = (
            report_data.get("id", f"{user_id}_{report_data.get('date', datetime.now().date().isoformat())}"),
            user_id,
            report_data.get("date", datetime.now().date().isoformat()),
            report_data.get("daily_effort_summary", ""),
            json.dumps(report_data.get("challenges", []), ensure_ascii=False),
            json.dumps(report_data.get("achievements", []), ensure_ascii=False),
            report_data.get("reflection", ""),
            report_data.get("goals_for_tomorrow", ""),
            report_data.get("mood_score"),
            report_data.get("created_at", datetime.now().isoformat()),
            report_data.get("updated_at", datetime.now().isoformat()),
        )

        self.sqlite_manager.execute_update(query, params)

    async def _ensure_default_user(self, user_id: str) -> None:
        """デフォルトユーザーの存在を確保"""
        # ユーザー存在チェック
        existing_user = self.sqlite_manager.execute_query(
            "SELECT google_id FROM users WHERE google_id = ?",
            (user_id,),
        )

        if not existing_user:
            # デフォルトユーザー作成
            query = """
            INSERT OR IGNORE INTO users (
                google_id, email, name, verified_email, created_at, last_login, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """

            now = datetime.now().isoformat()
            params = (
                user_id,
                f"{user_id}@example.com",
                user_id.replace("_", " ").title(),
                False,
                now,
                now,
                now,
            )

            self.sqlite_manager.execute_update(query, params)
            self.logger.debug(f"デフォルトユーザー作成: {user_id}")

    async def backup_json_data(self, backup_dir: Path | None = None) -> dict[str, Any]:
        """既存JSONデータのバックアップ"""
        backup_dir = backup_dir or (self.data_dir / "backup" / datetime.now().strftime("%Y%m%d_%H%M%S"))
        backup_dir.mkdir(parents=True, exist_ok=True)

        self.logger.info(f"JSONデータバックアップ開始: {backup_dir}")

        result = {"backed_up_files": [], "errors": []}

        try:
            # JSONファイルをコピー
            for json_file in self.data_dir.glob("*.json"):
                try:
                    backup_file = backup_dir / json_file.name
                    backup_file.write_text(json_file.read_text(encoding="utf-8"), encoding="utf-8")
                    result["backed_up_files"].append(json_file.name)
                    self.logger.debug(f"バックアップ完了: {json_file.name}")
                except Exception as e:
                    error_msg = f"バックアップエラー ({json_file.name}): {e}"
                    result["errors"].append(error_msg)
                    self.logger.warning(error_msg)

            self.logger.info(f"JSONデータバックアップ完了: {len(result['backed_up_files'])}ファイル")
            return result

        except Exception as e:
            self.logger.error(f"JSONデータバックアップエラー: {e}")
            result["errors"].append(str(e))
            return result

    async def get_migration_status(self) -> dict[str, Any]:
        """移行状況の確認"""
        try:
            # SQLiteテーブルのレコード数確認
            tables_status = {}

            for table in ["users", "family_info", "growth_records", "effort_reports"]:
                try:
                    result = self.sqlite_manager.execute_query(f"SELECT COUNT(*) as count FROM {table}")
                    tables_status[table] = result[0]["count"] if result else 0
                except Exception as e:
                    tables_status[table] = f"Error: {e}"

            # JSONファイル存在確認
            json_files = list(self.data_dir.glob("*.json"))

            return {
                "sqlite_records": tables_status,
                "json_files_count": len(json_files),
                "json_files": [f.name for f in json_files],
            }

        except Exception as e:
            self.logger.error(f"移行状況確認エラー: {e}")
            return {"error": str(e)}
