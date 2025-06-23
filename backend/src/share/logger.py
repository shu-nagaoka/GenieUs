import json
import logging
import os
from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING

from colorama import Fore, Style, init

# AppSettings のインポートを TYPE_CHECKING ブロック内に移動
if TYPE_CHECKING:
    pass

init(autoreset=True)


class ColoredJsonFormatter(logging.Formatter):
    """JSONログをカラー表示するためのカスタムフォーマッタクラス"""

    COLORS = {
        "DEBUG": Fore.CYAN,
        "INFO": Fore.GREEN,
        "WARNING": Fore.YELLOW,
        "ERROR": Fore.RED,
        "CRITICAL": Fore.RED + Style.BRIGHT,
    }

    def format(self, record: logging.LogRecord) -> str:
        """ログレコードをJSON形式にフォーマットし、カラー表示を適用する"""
        JST = timezone(timedelta(hours=+9), "JST")
        jst_time = datetime.now(JST)

        log_record = {
            "timestamp": jst_time.isoformat(timespec="microseconds"),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)

        formatted_json = json.dumps(log_record, indent=4, ensure_ascii=False)

        color = self.COLORS.get(record.levelname, Fore.WHITE)
        return f"{color}{formatted_json}{Style.RESET_ALL}"


def setup_logger(name: str, env: str = "", log_level: int | None = None) -> logging.Logger:
    """指定された名前とログレベルでロガーを設定します。

    環境変数に基づいて適切なログレベルを設定し、ストリームハンドラとファイルハンドラを追加します。
    開発環境では詳細なデバッグログを出力し、ファイルにも保存します。

    Args:
        name (str): ロガーの名前
        log_level (Optional[int]): ログレベル。Noneの場合は環境変数に基づいて自動設定

    Returns:
        logging.Logger: 設定されたロガーインスタンス

    """
    logger = logging.getLogger(name)
    is_store_local = False

    if log_level is None:
        if env == "dev" or env == "dev":
            log_level = logging.DEBUG
            is_store_local = True
        elif env == "production":
            log_level = logging.INFO
            is_store_local = False
        else:  # staging 等 今後追加される環境
            log_level = logging.INFO
            is_store_local = False

    if log_level is None:
        log_level = logging.INFO

    logger.setLevel(log_level)

    if logger.hasHandlers():
        logger.handlers.clear()

    # ストリーム出力用
    json_formatter = ColoredJsonFormatter()
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(json_formatter)
    logger.addHandler(stream_handler)

    # ファイル出力用
    if is_store_local:
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        logs_dir = os.path.join(project_root, "logs")
        os.makedirs(logs_dir, exist_ok=True)
        log_file_path = os.path.join(logs_dir, f"{name}.log")
        file_handler = logging.FileHandler(log_file_path)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    logger.propagate = False

    return logger
