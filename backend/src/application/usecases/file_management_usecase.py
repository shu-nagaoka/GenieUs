"""ファイル管理UseCase"""

import logging
from typing import Any

from src.application.interface.protocols.file_operator import FileOperatorProtocol


class FileManagementUseCase:
    """ファイル操作のビジネスロジック"""

    def __init__(self, file_operator: FileOperatorProtocol, logger: logging.Logger):
        self.file_operator = file_operator
        self.logger = logger

    def upload_child_file(
        self,
        bucket_name: str,
        file_name: str,
        file_data: Any,
        child_id: str,
        file_type: str = "image",
        content_type: str | None = None,
    ) -> dict[str, Any]:
        """子どもに関連するファイルをアップロード

        Args:
            bucket_name: GCSバケット名
            file_name: ファイル名
            file_data: ファイルデータ
            child_id: 子どものID
            file_type: ファイルタイプ (image, document, video等)
            content_type: コンテンツタイプ

        Returns:
            Dict[str, Any]: アップロード結果

        """
        try:
            self.logger.info(
                f"ファイルアップロード開始: child_id={child_id}, file_name={file_name}, file_type={file_type}",
            )

            # ビジネスロジック: ディレクトリ構造の決定
            directory = self._determine_upload_directory(child_id, file_type)

            # ビジネスロジック: ファイル名の正規化
            normalized_file_name = self._normalize_file_name(file_name, child_id)

            # Infrastructure層でのアップロード実行
            upload_path = self.file_operator.upload_file(
                bucket_name=bucket_name,
                file_name=normalized_file_name,
                data=file_data,
                content_type=content_type,
                directory=directory,
            )

            if upload_path:
                result = {
                    "success": True,
                    "upload_path": upload_path,
                    "file_name": normalized_file_name,
                    "directory": directory,
                    "child_id": child_id,
                    "file_type": file_type,
                }
                self.logger.info(f"ファイルアップロード完了: {upload_path}")
                return result
            else:
                return self._create_upload_error_response("アップロードに失敗しました")

        except Exception as e:
            self.logger.error(f"ファイルアップロードUseCase実行エラー: {e}")
            return self._create_upload_error_response(str(e))

    def download_child_file(
        self,
        bucket_name: str,
        file_name: str,
        child_id: str,
        file_type: str = "image",
        as_text: bool = False,
    ) -> dict[str, Any]:
        """子どもに関連するファイルをダウンロード

        Args:
            bucket_name: GCSバケット名
            file_name: ファイル名
            child_id: 子どものID
            file_type: ファイルタイプ
            as_text: テキストとしてダウンロードするか

        Returns:
            Dict[str, Any]: ダウンロード結果とファイルデータ

        """
        try:
            self.logger.info(f"ファイルダウンロード開始: child_id={child_id}, file_name={file_name}, as_text={as_text}")

            # ビジネスロジック: ディレクトリ構造の決定
            directory = self._determine_upload_directory(child_id, file_type)

            # Infrastructure層でのダウンロード実行
            if as_text:
                file_data = self.file_operator.download_file_as_text(
                    bucket_name=bucket_name,
                    file_name=file_name,
                    directory=directory,
                )
            else:
                file_data = self.file_operator.download_file(
                    bucket_name=bucket_name,
                    file_name=file_name,
                    directory=directory,
                )

            result = {
                "success": True,
                "file_data": file_data,
                "file_name": file_name,
                "directory": directory,
                "child_id": child_id,
                "file_type": file_type,
                "data_type": "text" if as_text else "binary",
            }

            data_size = len(file_data) if file_data else 0
            self.logger.info(f"ファイルダウンロード完了: size={data_size}bytes")
            return result

        except FileNotFoundError:
            return self._create_download_error_response("ファイルが見つかりません")
        except Exception as e:
            self.logger.error(f"ファイルダウンロードUseCase実行エラー: {e}")
            return self._create_download_error_response(str(e))

    def list_child_files(self, bucket_name: str, child_id: str, file_type: str | None = None) -> dict[str, Any]:
        """子どもに関連するファイル一覧を取得

        Args:
            bucket_name: GCSバケット名
            child_id: 子どものID
            file_type: ファイルタイプ（指定しない場合は全て）

        Returns:
            Dict[str, Any]: ファイル一覧

        """
        try:
            self.logger.info(f"ファイル一覧取得開始: child_id={child_id}, file_type={file_type}")

            # ビジネスロジック: 検索ディレクトリの決定
            if file_type:
                directory = self._determine_upload_directory(child_id, file_type)
            else:
                directory = f"children/{child_id}"  # 子ども全体のディレクトリ

            # Infrastructure層でのファイル一覧取得
            files = self.file_operator.list_files(bucket_name=bucket_name, directory=directory)

            # ビジネスロジック: ファイル情報の整理・フィルタリング
            organized_files = self._organize_file_list(files, child_id)

            result = {
                "success": True,
                "child_id": child_id,
                "file_type": file_type,
                "directory": directory,
                "files": organized_files,
                "total_count": len(organized_files),
            }

            self.logger.info(f"ファイル一覧取得完了: {len(organized_files)}件")
            return result

        except Exception as e:
            self.logger.error(f"ファイル一覧取得UseCase実行エラー: {e}")
            return {"success": False, "error": str(e), "child_id": child_id, "files": [], "total_count": 0}

    def _determine_upload_directory(self, child_id: str, file_type: str) -> str:
        """アップロード先ディレクトリの決定"""
        base_dir = f"children/{child_id}"

        type_mapping = {
            "image": "images",
            "video": "videos",
            "document": "documents",
            "audio": "audio",
            "medical": "medical_records",
        }

        sub_dir = type_mapping.get(file_type, "others")
        return f"{base_dir}/{sub_dir}"

    def _normalize_file_name(self, file_name: str, child_id: str) -> str:
        """ファイル名の正規化"""
        import re
        from datetime import datetime

        # 特殊文字の除去
        safe_name = re.sub(r"[^\w\-_\.]", "_", file_name)

        # タイムスタンプの追加（重複防止）
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        name_parts = safe_name.rsplit(".", 1)

        if len(name_parts) == 2:
            base_name, extension = name_parts
            return f"{child_id}_{timestamp}_{base_name}.{extension}"
        else:
            return f"{child_id}_{timestamp}_{safe_name}"

    def _organize_file_list(self, files: list[dict[str, Any]], child_id: str) -> list[dict[str, Any]]:
        """ファイル一覧の整理"""
        organized = []

        for file_info in files:
            # ビジネスロジック: ファイル情報の拡張
            organized_file = {
                **file_info,
                "child_id": child_id,
                "file_category": self._categorize_file(file_info.get("name", "")),
                "size_mb": round(file_info.get("size", 0) / (1024 * 1024), 2),
            }
            organized.append(organized_file)

        # 更新日時順でソート
        organized.sort(key=lambda x: x.get("update_at", ""), reverse=True)
        return organized

    def _categorize_file(self, file_name: str) -> str:
        """ファイルのカテゴリ分類"""
        name_lower = file_name.lower()

        if any(ext in name_lower for ext in [".jpg", ".jpeg", ".png", ".gif"]):
            return "image"
        elif any(ext in name_lower for ext in [".mp4", ".avi", ".mov"]):
            return "video"
        elif any(ext in name_lower for ext in [".pdf", ".doc", ".txt"]):
            return "document"
        elif any(ext in name_lower for ext in [".mp3", ".wav", ".m4a"]):
            return "audio"
        else:
            return "other"

    def _create_upload_error_response(self, error_message: str) -> dict[str, Any]:
        """アップロードエラーレスポンス作成"""
        return {"success": False, "error": error_message, "upload_path": "", "file_name": "", "directory": ""}

    def _create_download_error_response(self, error_message: str) -> dict[str, Any]:
        """ダウンロードエラーレスポンス作成"""
        return {"success": False, "error": error_message, "file_data": None, "file_name": "", "directory": ""}
