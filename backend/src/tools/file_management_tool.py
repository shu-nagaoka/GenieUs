"""ファイル管理Tool - UseCase層の薄いラッパー"""

import logging
from typing import Any

from google.adk.tools import FunctionTool

from src.application.usecases.file_management_usecase import FileManagementUseCase


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
        child_id: str,
        bucket_name: str = "genie-child-records",
        file_name: str = "",
        file_type: str = "image",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """子どもに関連するファイルの管理操作

        Args:
            operation: 操作タイプ（upload, download, list）
            child_id: 子どものID
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
                    return {
                        "success": True,
                        "response": _create_file_list_response(files, child_id),
                        "file_data": result,
                        "metadata": {
                            "operation": operation,
                            "child_id": child_id,
                            "total_files": len(files),
                        },
                    }
                else:
                    return _create_error_response(operation, result.get("error", "ファイル一覧取得に失敗"))

            elif operation == "download":
                # ファイルダウンロード
                if not file_name:
                    return _create_error_response(operation, "ファイル名が指定されていません")

                as_text = kwargs.get("as_text", False)
                result = file_management_usecase.download_child_file(
                    bucket_name=bucket_name,
                    file_name=file_name,
                    child_id=child_id,
                    file_type=file_type,
                    as_text=as_text,
                )

                if result.get("success"):
                    return {
                        "success": True,
                        "response": f"ファイル「{file_name}」のダウンロードが完了しました。",
                        "file_data": result,
                        "metadata": {
                            "operation": operation,
                            "child_id": child_id,
                            "file_name": file_name,
                            "data_size": len(result.get("file_data", b"")),
                        },
                    }
                else:
                    return _create_error_response(operation, result.get("error", "ファイルダウンロードに失敗"))

            elif operation == "upload":
                # ファイルアップロード（通常はWebAPIから呼ばれるため、ここでは情報のみ）
                return {
                    "success": True,
                    "response": "ファイルアップロード機能は利用可能です。WebUIまたはAPIを通じてファイルをアップロードしてください。",
                    "metadata": {
                        "operation": operation,
                        "child_id": child_id,
                        "supported_types": ["image", "video", "document", "audio"],
                    },
                }

            else:
                return _create_error_response(operation, f"サポートされていない操作です: {operation}")

        except Exception as e:
            logger.error(f"ファイル管理ツール実行エラー: {e}")
            return _create_error_response(operation, f"ファイル操作中にエラーが発生しました: {e!s}")

    def _create_file_list_response(files: list[dict[str, Any]], child_id: str) -> str:
        """ファイル一覧を自然言語レスポンスに変換"""
        if not files:
            return f"お子さん（ID: {child_id}）に関連するファイルは見つかりませんでした。"

        response_parts = [
            f"お子さん（ID: {child_id}）に関連するファイルを{len(files)}件見つけました。",
            "",
        ]

        # ファイルタイプ別の集計
        type_counts = {}
        for file_info in files:
            file_category = file_info.get("file_category", "other")
            type_counts[file_category] = type_counts.get(file_category, 0) + 1

        # タイプ別サマリー
        type_summary = []
        for file_type, count in type_counts.items():
            type_name = {
                "image": "画像",
                "video": "動画",
                "document": "文書",
                "audio": "音声",
                "other": "その他",
            }.get(file_type, file_type)
            type_summary.append(f"{type_name}: {count}件")

        response_parts.append("📁 ファイル種類別: " + "、".join(type_summary))

        # 最新ファイルの表示（最大5件）
        if files:
            response_parts.append("\n📋 最新ファイル:")
            for i, file_info in enumerate(files[:5]):
                name = file_info.get("name", "")
                size_mb = file_info.get("size_mb", 0)
                update_time = str(file_info.get("update_at", ""))[:10]  # 日付部分のみ
                response_parts.append(f"  {i + 1}. {name} ({size_mb}MB) - {update_time}")

        return "\n".join(response_parts)

    def _create_error_response(operation: str, error_message: str) -> dict[str, Any]:
        """エラーレスポンス作成"""
        return {
            "success": False,
            "response": f"ファイル{operation}操作でエラーが発生しました: {error_message}",
            "metadata": {"operation": operation, "error": error_message},
        }

    logger.info("ファイル管理ツール作成完了")
    return FunctionTool(func=manage_child_files)
