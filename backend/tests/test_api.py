#!/usr/bin/env python3
"""APIエンドポイントのE2Eテストスクリプト"""

import sys
import time
from pathlib import Path

import requests

# プロジェクトルートを追加
sys.path.append(str(Path(__file__).parent.parent / "src"))

from src.share.logger import setup_logger

logger = setup_logger(__name__)

BASE_URL = "http://localhost:8000"


def test_health_endpoint():
    """ヘルスチェックエンドポイントテスト"""
    try:
        response = requests.get(f"{BASE_URL}/api/v1/health")
        if response.status_code == 200:
            logger.info("✅ ヘルスチェック成功")
            return True
        else:
            logger.error(f"❌ ヘルスチェック失敗: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"❌ ヘルスチェックエラー: {e}")
        return False


def test_multiagent_chat_api():
    """マルチエージェントチャットAPIのE2Eテスト"""
    try:
        payload = {
            "message": "夜泣きで困っています。生後3ヶ月です。",
            "user_id": "test_user_api",
            "session_id": "test_session_api_001",
            "requested_agent": "childcare",
        }

        headers = {"Content-Type": "application/json"}

        logger.info("マルチエージェントチャットAPI実行開始")
        response = requests.post(
            f"{BASE_URL}/api/v1/multiagent/chat",
            json=payload,
            headers=headers,
            timeout=30,
        )

        if response.status_code == 200:
            data = response.json()
            logger.info("✅ マルチエージェントチャットAPI成功")
            logger.info(f"レスポンス: {data['response'][:100]}...")
            logger.info(f"ステータス: {data['status']}")
            logger.info(f"セッションID: {data['session_id']}")
            logger.info(f"使用エージェント: {data.get('agent_used', 'unknown')}")
            logger.info(f"エージェント情報: {data.get('agent_info', {})}")
            return True
        else:
            logger.error(f"❌ マルチエージェントチャットAPI失敗: {response.status_code}")
            logger.error(f"エラー内容: {response.text}")
            return False

    except Exception as e:
        logger.error(f"❌ マルチエージェントチャットAPIエラー: {e}")
        return False


def main():
    """メインテスト実行"""
    logger.info("🚀 API E2Eテスト開始")

    # サーバーの起動待ち
    logger.info("サーバー接続確認中...")
    time.sleep(2)

    results = [
        test_health_endpoint(),
        test_multiagent_chat_api(),
    ]

    success_count = sum(results)
    total_count = len(results)

    logger.info(f"🎯 テスト結果: {success_count}/{total_count} 成功")

    if success_count == total_count:
        logger.info("🎉 API E2Eテストが全て成功しました！")
        return 0
    else:
        logger.error("❌ 一部APIテストが失敗しました")
        return 1


if __name__ == "__main__":
    import sys

    sys.exit(main())
