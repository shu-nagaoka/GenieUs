"""ファイル管理Tool - UseCase層の薄いラッパー"""

import logging
from typing import Any

from google.adk.tools import FunctionTool

from src.application.usecases.file_management_usecase import FileManagementUseCase
from src.tools.common_response_formatter import ChildcareResponseFormatter


def create_file_management_tool(
    file_management_usecase: FileManagementUseCase,
    logger: logging.Logger,
) -> FunctionTool:
    """ファイル管理ツール作成（薄いアダプター）

    Args:
        file_management_usecase: ファイル管理UseCase
        logger: ロガー（DIコンテナから注入）

    Returns:
        FunctionTool: ADK用ファイル管理ツール

    """
    logger.info("ファイル管理ツール作成開始")

    def manage_child_files(
        operation: str,
        child_id: str = "default_child",
        bucket_name: str = "genie-child-records",
        file_name: str = "",
        file_type: str = "image",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """子どもに関連するファイルの管理操作

        Args:
            operation: 操作タイプ（upload, download, list）
            child_id: 子どものID（デフォルト: "default_child"）
            bucket_name: GCSバケット名
            file_name: ファイル名（upload, downloadで必要）
            file_type: ファイルタイプ（image, video, document等）
            **kwargs: 追加パラメータ

        Returns:
            Dict[str, Any]: 操作結果

        """
        try:
            logger.info(
                f"ファイル管理ツール実行開始: operation={operation}, child_id={child_id}, file_type={file_type}",
            )

            if operation == "list":
                # ファイル一覧取得
                result = file_management_usecase.list_child_files(
                    bucket_name=bucket_name,
                    child_id=child_id,
                    file_type=file_type if file_type != "all" else None,
                )

                if result.get("success"):
                    files = result.get("files", [])
                    if not files:
                        return ChildcareResponseFormatter.error_response(
                            "ファイル一覧取得", "該当するファイルが見つかりませんでした", child_id
                        ).to_dict()

                    # 最初のファイル情報を使用
                    first_file = files[0]
                    return ChildcareResponseFormatter.file_management_success(
                        operation="ファイル一覧取得",
                        file_info={"name": f"{len(files)}件のファイル", "size": sum(f.get("size", 0) for f in files)},
                        child_id=child_id,
                    ).to_dict()
                else:
                    return ChildcareResponseFormatter.error_response(
                        "ファイル一覧取得", result.get("error", "ファイル一覧取得に失敗"), child_id
                    ).to_dict()

            elif operation == "download":
                # ファイルダウンロード
                if not file_name:
                    return ChildcareResponseFormatter.error_response(
                        "ファイルダウンロード", "ファイル名が指定されていません", child_id
                    ).to_dict()

                as_text = kwargs.get("as_text", False)
                result = file_management_usecase.download_child_file(
                    bucket_name=bucket_name,
                    file_name=file_name,
                    child_id=child_id,
                    file_type=file_type,
                    as_text=as_text,
                )

                if result.get("success"):
                    data_size = len(result.get("file_data", b""))
                    return ChildcareResponseFormatter.file_management_success(
                        operation="ファイルダウンロード",
                        file_info={"name": file_name, "size": data_size},
                        child_id=child_id,
                    ).to_dict()
                else:
                    return ChildcareResponseFormatter.error_response(
                        "ファイルダウンロード", result.get("error", "ファイルダウンロードに失敗"), child_id
                    ).to_dict()

            elif operation == "upload":
                # ファイルアップロード（通常はWebAPIから呼ばれるため、ここでは情報のみ）
                return ChildcareResponseFormatter.file_management_success(
                    operation="ファイルアップロード情報",
                    file_info={"name": "アップロード機能", "size": 0},
                    child_id=child_id,
                ).to_dict()

            else:
                return ChildcareResponseFormatter.error_response(
                    "ファイル管理", f"サポートされていない操作です: {operation}", child_id
                ).to_dict()

        except Exception as e:
            logger.error(f"ファイル管理ツール実行エラー: {e}")
            return ChildcareResponseFormatter.error_response(
                "ファイル管理", f"ファイル操作中にエラーが発生しました: {e!s}", child_id
            ).to_dict()

    def _get_file_type_summary(files: list[dict[str, Any]]) -> dict[str, int]:
        """ファイルタイプ別の集計を取得"""
        type_counts = {}
        for file_info in files:
            file_category = file_info.get("file_category", "other")
            type_counts[file_category] = type_counts.get(file_category, 0) + 1
        return type_counts

    logger.info("ファイル管理ツール作成完了")
    return FunctionTool(func=manage_child_files)
