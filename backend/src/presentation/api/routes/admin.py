"""管理者用API - データ移行・システム管理"""

from typing import Any

from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel

# ========== Response Models ==========

class MigrationStatusResponse(BaseModel):
    """移行状況レスポンス"""

    sqlite_records: dict[str, Any]
    json_files_count: int
    json_files: list[str]


class MigrationResultResponse(BaseModel):
    """移行結果レスポンス"""

    success: bool
    migrated_files: list[str] = []
    errors: list[str] = []
    summary: dict[str, Any] = {}


# ========== API Router ==========

router = APIRouter()


# ========== 管理用エンドポイント ==========

@router.get("/migration/status", response_model=MigrationStatusResponse)
async def get_migration_status(request: Request):
    """データ移行状況確認"""
    try:
        composition_root = request.app.composition_root
        data_migrator = composition_root.get_data_migrator()

        status = await data_migrator.get_migration_status()

        if "error" in status:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=status["error"],
            )

        return MigrationStatusResponse(**status)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"移行状況確認エラー: {e!s}",
        )


@router.post("/migration/backup")
async def backup_json_data(request: Request):
    """JSONデータのバックアップ"""
    try:
        composition_root = request.app.composition_root
        data_migrator = composition_root.get_data_migrator()

        result = await data_migrator.backup_json_data()

        if result.get("errors"):
            return {
                "success": False,
                "backed_up_files": result["backed_up_files"],
                "errors": result["errors"],
            }

        return {
            "success": True,
            "backed_up_files": result["backed_up_files"],
            "message": f"{len(result['backed_up_files'])}ファイルをバックアップしました",
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"バックアップエラー: {e!s}",
        )


@router.post("/migration/execute", response_model=MigrationResultResponse)
async def execute_data_migration(request: Request):
    """データ移行実行"""
    try:
        composition_root = request.app.composition_root
        data_migrator = composition_root.get_data_migrator()
        logger = composition_root.logger

        logger.info("管理者によるデータ移行実行開始")

        # データ移行実行
        result = await data_migrator.migrate_all_data()

        if result["success"]:
            logger.info("データ移行実行完了", extra={
                "total_migrated": sum(
                    summary.get("migrated_count", 0)
                    for summary in result["summary"].values()
                ),
            })
        else:
            logger.warning("データ移行実行でエラー発生", extra={
                "errors": result["errors"],
            })

        return MigrationResultResponse(**result)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"データ移行実行エラー: {e!s}",
        )


@router.get("/database/info")
async def get_database_info(request: Request):
    """データベース情報取得"""
    try:
        composition_root = request.app.composition_root
        sqlite_manager = composition_root.get_sqlite_manager()
        database_migrator = composition_root.get_database_migrator()

        # データベース初期化状況
        is_initialized = database_migrator.is_database_initialized()

        # マイグレーション履歴
        migration_history = database_migrator.check_migration_status()

        # テーブル一覧と件数
        tables_info = {}
        tables = ["users", "family_info", "child_records", "growth_records",
                 "memory_records", "schedule_events", "effort_reports", "meal_plans"]

        for table in tables:
            try:
                result = sqlite_manager.execute_query(f"SELECT COUNT(*) as count FROM {table}")
                tables_info[table] = result[0]["count"] if result else 0
            except Exception as e:
                tables_info[table] = f"Error: {e!s}"

        return {
            "database_initialized": is_initialized,
            "migration_history": migration_history,
            "tables_info": tables_info,
            "database_path": str(sqlite_manager.db_path),
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"データベース情報取得エラー: {e!s}",
        )


@router.post("/database/initialize")
async def initialize_database(request: Request):
    """データベース初期化"""
    try:
        composition_root = request.app.composition_root
        database_migrator = composition_root.get_database_migrator()
        logger = composition_root.logger

        logger.info("管理者によるデータベース初期化実行")

        # データベース初期化
        database_migrator.initialize_database()

        logger.info("データベース初期化完了")

        return {
            "success": True,
            "message": "データベースが初期化されました",
        }

    except Exception as e:
        logger.error(f"データベース初期化エラー: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"データベース初期化エラー: {e!s}",
        )


@router.get("/system/health")
async def get_system_health(request: Request):
    """システムヘルスチェック"""
    try:
        composition_root = request.app.composition_root

        health_status = {
            "database": "unknown",
            "composition_root": "ok",
            "authentication": "unknown",
            "components": {},
        }

        # データベース接続チェック
        try:
            sqlite_manager = composition_root.get_sqlite_manager()
            sqlite_manager.execute_query("SELECT 1")
            health_status["database"] = "ok"
        except Exception as e:
            health_status["database"] = f"error: {e!s}"

        # 認証コンポーネントチェック
        try:
            auth_middleware = composition_root.get_auth_middleware()
            health_status["authentication"] = "ok"
        except Exception as e:
            health_status["authentication"] = f"error: {e!s}"

        # 各コンポーネントの存在確認
        components = [
            "user_repository", "data_migrator", "database_migrator",
            "google_verifier", "jwt_authenticator",
        ]

        for component in components:
            try:
                composition_root._infrastructure.get(component)
                health_status["components"][component] = "ok"
            except Exception as e:
                health_status["components"][component] = f"error: {e!s}"

        return {
            "overall_status": "ok" if all(
                status == "ok" for status in [
                    health_status["database"],
                    health_status["composition_root"],
                    health_status["authentication"],
                ]
            ) else "degraded",
            "details": health_status,
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"ヘルスチェックエラー: {e!s}",
        )
