import json
import logging
from typing import Any

from google.cloud import storage

from src.application.interface.protocols.file_operator import FileOperatorProtocol


class GcsFileOperator(FileOperatorProtocol):
    """GCSのファイル操作を行う実装クラス"""

    def __init__(self, project_id: str, logger: logging.Logger):
        try:
            self.logger = logger
            self.logger.info(f"GCSFileOperatorを初期化します。プロジェクトID: {project_id}")
            self.gcs_client = storage.Client(project_id)
            self.logger.info("GCSFileOperatorの初期化が完了しました")
        except Exception as e:
            logger.error(f"GCSFileOperatorの初期化中にエラーが発生しました: {e!s}")
            raise

    def list_buckets(self) -> list:
        """利用可能なバケットの一覧を取得します"""
        self.logger.info("バケット一覧の取得を開始します")
        try:
            bucket_list = []
            all_bucket = self.gcs_client.list_buckets()

            if not all_bucket:
                self.logger.warning("プロジェクト内にバケットが存在しません")
                return []

            for bucket in all_bucket:
                bucket_dict = {
                    "name": bucket.name,
                    "region": bucket.location,
                    "create_at": bucket.time_created,
                    "storage_type": bucket.storage_class,
                }
                bucket_list.append(bucket_dict)

            bucket_count = len(bucket_list)
            self.logger.info(f"バケット一覧の取得が完了しました。取得バケット数: {bucket_count}")
            self.logger.debug(f"最初の3つのバケット: {bucket_list[:3] if bucket_count >= 3 else bucket_list}")
            return bucket_list

        except Exception as e:
            self.logger.error(f"バケット一覧の取得中にエラーが発生しました: {e!s}")
            raise

    def check_file_size(self, size: int, file_name: str, file_size: int) -> bool:
        """ファイルサイズが制限内かどうかをチェックします"""
        size_mb = round(size / (1024 * 1024), 2)
        max_size_mb = round(file_size / (1024 * 1024), 2)

        self.logger.debug(
            f"ファイルサイズをチェックします: {file_name}, サイズ: {size_mb}MB, 最大許容サイズ: {max_size_mb}MB",
        )

        if size > file_size:
            self.logger.warning(
                f"ファイルサイズが上限を超えています: {file_name}, サイズ: {size_mb}MB, 上限: {max_size_mb}MB",
            )
            return False
        else:
            self.logger.debug(f"ファイルサイズは許容範囲内です: {file_name}, サイズ: {size_mb}MB")
            return True

    def list_files(self, bucket_name: str, directory: str | None = None) -> list[dict[str, Any]]:
        """指定されたバケット内のファイル一覧を取得します"""
        target = f"{bucket_name}/{directory if directory else ''}"
        self.logger.info(f"ファイル一覧の取得を開始します。対象: {target}")

        try:
            file_list = []

            if directory:
                self.logger.debug(f"指定ディレクトリのファイルを検索します: {directory}")
                bucket = self.gcs_client.bucket(bucket_name)
                all_file = bucket.list_blobs(prefix=directory)
            else:
                self.logger.debug(f"バケット全体のファイルを検索します: {bucket_name}")
                all_file = self.gcs_client.list_blobs(bucket_name)

            file_count = 0
            total_size = 0

            for file in all_file:
                file_dict = {
                    "name": file.name,
                    "size": file.size,
                    "content_type": file.content_type,
                    "create_at": file.time_created,
                    "update_at": file.updated,
                    "metadata": file.metadata,
                }
                file_list.append(file_dict)
                file_count += 1
                total_size += file.size

            if file_count == 0:
                self.logger.warning(f"指定した場所にファイルが存在しません: {target}")
                return []

            total_size_mb = round(total_size / (1024 * 1024), 2)
            self.logger.info(
                f"ファイル一覧の取得が完了しました。ファイル数: {file_count}, 合計サイズ: {total_size_mb}MB",
            )
            return file_list

        except Exception as e:
            self.logger.error(f"ファイル一覧の取得中にエラーが発生しました: {target}, エラー: {e!s}")
            raise

    def upload_file(
        self,
        bucket_name: str,
        file_name: str,
        data: Any,
        content_type: str | None = "",
        directory: str | None = "",
    ) -> str:
        """ファイルをGCSにアップロードします"""
        try:
            if directory:
                blob_object = f"{directory}/{file_name}"
            else:
                blob_object = f"{file_name}"

            target_path = f"gs://{bucket_name}/{blob_object}"
            self.logger.info(f"ファイルのアップロードを開始します: {target_path}")

            # データサイズの計算（大まかな推定）
            if isinstance(data, (dict, list)):
                data_size = len(json.dumps(data, ensure_ascii=False))
            elif isinstance(data, str):
                data_size = len(data)
            else:
                data_size = -1  # サイズ不明

            if data_size > 0:
                data_size_kb = round(data_size / 1024, 2)
                self.logger.debug(f"アップロードするデータサイズ: {data_size_kb}KB, データ型: {type(data).__name__}")

            bucket = self.gcs_client.bucket(bucket_name)
            blob = bucket.blob(blob_object)

            # 既存ファイルのチェック
            if blob.exists():
                self.logger.debug(f"既存ファイルを上書きします: {target_path}")

            result = self._check_upload_file_type(blob, data, content_type, num_retries=3)  # type: ignore
            self.logger.info(f"ファイルのアップロードが完了しました: {target_path}")

            return target_path

        except Exception as e:
            self.logger.error(
                f"ファイルのアップロード中にエラーが発生しました: {bucket_name}/{file_name}, エラー: {e!s}",
            )
            return ""

    def _check_upload_file_type(self, blob: Any, data: Any, content_type: str, num_retries: int) -> None:
        """データ型に応じて適切なアップロード方法を選択します"""
        try:
            self.logger.debug(
                f"アップロードデータ型: {type(data).__name__}, content_type: {content_type}, リトライ設定: {num_retries}",
            )

            if isinstance(data, dict):
                self.logger.debug("辞書型データをJSONとしてアップロードします")
                json_data = json.dumps(data, ensure_ascii=False, indent=4)
                blob.upload_from_string(json_data, content_type="application/json", num_retries=num_retries)

            elif isinstance(data, list):
                self.logger.debug("リスト型データをJSONとしてアップロードします")
                json_data = json.dumps(data, ensure_ascii=False, indent=4)
                blob.upload_from_string(json_data, content_type="application/json", num_retries=num_retries)

            elif isinstance(data, str):
                self.logger.debug("文字列データをアップロードします")
                if content_type == "text/plain":
                    blob.upload_from_string(data, content_type="text/plain", num_retries=num_retries)
                    self.logger.debug("テキストファイルとしてアップロード完了")
                else:
                    blob.upload_from_string(data, content_type="application/json", num_retries=num_retries)
                    self.logger.debug("JSONファイルとしてアップロード完了")

            elif isinstance(data, bytes):
                self.logger.debug("Bytes型データをアップロードします")
                if content_type == "image/jpeg" or content_type == "image/png":
                    blob.upload_from_string(data, content_type=content_type, num_retries=num_retries)
                    self.logger.debug(f"画像ファイルとしてアップロード完了: {content_type}")
                elif content_type == "text/plain":
                    blob.upload_from_string(data, content_type=content_type, num_retries=num_retries)
                    self.logger.debug("テキストファイルとしてアップロード完了")
                else:
                    blob.upload_from_string(data, content_type="video/mp4", num_retries=num_retries)
            else:
                self.logger.error(f"サポートされないデータ型です: {type(data).__name__}")
                raise ValueError(f"サポートされないデータ型です: {type(data).__name__}")

        except Exception as e:
            self.logger.error(f"データ型チェック中にエラーが発生しました: {e!s}")
            raise

    def download_file(self, bucket_name: str, file_name: str, directory: str | None = None) -> bytes:
        """ファイルをバイナリデータとしてダウンロードします"""
        try:
            if directory:
                blob_object = f"{directory}/{file_name}"
            else:
                blob_object = f"{file_name}"

            source_path = f"gs://{bucket_name}/{blob_object}"
            self.logger.info(f"ファイルのバイナリダウンロードを開始します: {source_path}")

            bucket = self.gcs_client.bucket(bucket_name)
            blob = bucket.blob(blob_object)

            if not blob.exists():
                self.logger.error(f"ダウンロード対象のファイルが存在しません: {source_path}")
                raise FileNotFoundError(f"ファイルが見つかりません: {blob_object}")

            self.logger.debug(f"ファイルのメタデータ: サイズ={blob.size}バイト, 更新日時={blob.updated}")
            downloaded_data = blob.download_as_bytes()

            data_size_kb = round(len(downloaded_data) / 1024, 2)
            self.logger.info(f"ファイルのバイナリダウンロードが完了しました: {source_path}, サイズ: {data_size_kb}KB")

            return downloaded_data

        except FileNotFoundError as e:
            self.logger.error(f"ファイルが見つかりません: {bucket_name}/{file_name}, エラー: {e!s}")
            raise
        except Exception as e:
            self.logger.error(
                f"ファイルのダウンロード中にエラーが発生しました: {bucket_name}/{file_name}, エラー: {e!s}",
            )
            return b""

    def download_file_as_text(self, bucket_name: str, file_name: str, directory: str | None = None) -> str:
        """ファイルをテキストデータとしてダウンロードします"""
        try:
            if directory:
                blob_object = f"{directory}/{file_name}"
            else:
                blob_object = f"{file_name}"

            source_path = f"gs://{bucket_name}/{blob_object}"
            self.logger.info(f"ファイルのテキストダウンロードを開始します: {source_path}")

            bucket = self.gcs_client.bucket(bucket_name)
            blob = bucket.blob(blob_object)

            if not blob.exists():
                self.logger.error(f"ダウンロード対象のファイルが存在しません: {source_path}")
                raise FileNotFoundError(f"ファイルが見つかりません: {blob_object}")

            self.logger.debug(f"ファイルのメタデータ: サイズ={blob.size}バイト, 更新日時={blob.updated}")
            downloaded_data = blob.download_as_text()

            data_size_kb = round(len(downloaded_data) / 1024, 2)
            self.logger.info(f"ファイルのテキストダウンロードが完了しました: {source_path}, サイズ: {data_size_kb}KB")

            return downloaded_data

        except FileNotFoundError as e:
            self.logger.error(f"ファイルが見つかりません: {bucket_name}/{file_name}, エラー: {e!s}")
            raise
        except Exception as e:
            self.logger.error(
                f"ファイルのテキストダウンロード中にエラーが発生しました: {bucket_name}/{file_name}, エラー: {e!s}",
            )
            return ""
