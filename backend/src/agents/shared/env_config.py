"""エージェント共通の環境変数設定

すべてのエージェントで統一的にVertex AI環境変数を読み込むための共通モジュール
"""

import logging
import os
from pathlib import Path
from typing import Dict, Any

import dotenv


def load_vertex_ai_config(logger: logging.Logger) -> Dict[str, Any]:
    """Vertex AI設定を環境変数から読み込む

    Args:
        logger: ロガー（DIコンテナから注入）

    Returns:
        Dict[str, Any]: Vertex AI設定情報
    """
    try:
        # 環境変数をローカル.envファイルから読み込み
        env_path = Path(__file__).parent.parent / "individual" / ".env"
        if env_path.exists():
            dotenv.load_dotenv(env_path)
            logger.info(f"環境変数ファイル読み込み: {env_path}")

        # 環境変数から直接読み込み
        vertex_enabled = os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "True").lower() == "true"
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
        location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")

        logger.info(f"Vertex AI設定確認: USE_VERTEXAI={vertex_enabled}, PROJECT={project_id}, LOCATION={location}")

        # Vertex AI設定を環境変数で確認
        if vertex_enabled and project_id:
            logger.info("Vertex AI設定確認完了")
            # 環境変数が設定されているので、ADKが自動的にVertex AIを使用
        else:
            logger.warning("Vertex AI設定が不完全です。")
            # ADKが利用可能な認証方法を自動選択

        return {
            "vertex_enabled": vertex_enabled,
            "project_id": project_id,
            "location": location,
            "config_valid": vertex_enabled and bool(project_id),
        }

    except Exception as e:
        logger.error(f"Vertex AI設定読み込みエラー: {e}")
        return {"vertex_enabled": False, "project_id": None, "location": "us-central1", "config_valid": False}
