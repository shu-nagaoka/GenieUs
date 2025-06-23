from typing import Any, Protocol


class FileOperatorProtocol(Protocol):
    """ファイル操作に関するプロトコルを定義するインターフェース

    このプロトコルは、アプリケーション内でのファイル操作（アップロード、ダウンロード、一覧取得など）
    に関する標準的なインターフェースを提供します。
    """

    def list_buckets(self) -> list:
        """利用可能なバケットの一覧を取得します

        Returns:
            List[str]: バケット情報のリスト

        """
        ...

    def check_file_size(self, size: int, file_name: str) -> bool:
        """ファイルサイズが制限内かどうかをチェックします

        Args:
            size: ファイルサイズ（バイト）
            file_name: ファイル名

        Returns:
            bool: サイズが制限内の場合はTrue、それ以外はFalse

        """
        ...

    def list_files(self, bucket_name: str, directory: str | None = None) -> list:
        """指定されたバケット内のファイル一覧を取得します

        Args:
            bucket_name: バケット名
            directory: ディレクトリパス（オプション）

        Returns:
            List[Dict[str]]: ファイル情報のリスト

        """
        ...

    def upload_file(
        self,
        bucket_name: str,
        file_name: str,
        data: Any,
        content_type: str | None = "",
        directory: str | None = "",
    ) -> str:
        """ファイルをGCSにアップロードします

        Args:
            bucket_name: バケット名
            file_name: ファイル名
            data: アップロードするデータ
            content_type: コンテンツタイプ（オプション）
            directory: ディレクトリパス（オプション）

        Returns:
            str: アップロードしたファイルのURIまたはパス

        """
        ...

    def download_file(self, bucket_name: str, file_name: str, directory: str | None = None) -> bytes:
        """ファイルをバイナリデータとしてダウンロードします

        Args:
            bucket_name: バケット名
            file_name: ファイル名
            directory: ディレクトリパス（オプション）

        Returns:
            bytes: ダウンロードしたファイルのバイナリデータ

        """
        ...

    def download_file_as_text(self, bucket_name: str, file_name: str, directory: str | None = None) -> str:
        """ファイルをテキストデータとしてダウンロードします

        Args:
            bucket_name: バケット名
            file_name: ファイル名
            directory: ディレクトリパス（オプション）

        Returns:
            str: ダウンロードしたファイルのテキストデータ

        """
        ...
