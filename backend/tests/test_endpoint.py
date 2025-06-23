#!/usr/bin/env python3
"""エンドポイント統合テストスクリプト"""

import asyncio
import sys
from pathlib import Path

# プロジェクトルートを追加
sys.path.append(str(Path(__file__).parent.parent / "src"))

from src.presentation.api.routes.multiagent_chat import MultiAgentChatMessage, multiagent_chat_endpoint
from src.di_provider.factory import get_container
from src.share.logger import setup_logger

logger = setup_logger(__name__)


async def test_multiagent_chat_endpoint():
    """マルチエージェントチャットエンドポイントのテスト"""
    logger.info("=== マルチエージェントチャットエンドポイント統合テスト開始 ===")

    try:
        # DIコンテナの初期化とワイヤリング
        container = get_container()
        container.wire(modules=["src.presentation.api.routes.multiagent_chat"])

        # AgentManagerの初期化
        agent_manager = container.agent_manager()
        agent_manager.initialize_all_agents()

        # テストメッセージ作成
        test_message = MultiAgentChatMessage(
            message="夜泣きで困っています。生後3ヶ月です。",
            user_id="test_user",
            session_id="test_session_001",
            requested_agent="childcare",
        )

        # エンドポイント実行（DI注入なしで直接呼び出し）
        logger.info("エンドポイント実行開始")
        response = await multiagent_chat_endpoint(test_message, agent_manager=agent_manager, logger=container.logger())

        # 結果確認
        logger.info("✅ エンドポイント実行成功")
        logger.info(f"レスポンス: {response.response[:100]}...")
        logger.info(f"ステータス: {response.status}")
        logger.info(f"使用エージェント: {response.agent_used}")
        logger.info(f"エージェント情報: {response.agent_info}")
        logger.info(f"フォローアップ質問数: {len(response.follow_up_questions or [])}")

        return True

    except Exception as e:
        logger.error(f"❌ エンドポイントテストエラー: {e}")
        import traceback

        logger.error(f"詳細: {traceback.format_exc()}")
        return False


async def main():
    """メインテスト実行"""
    logger.info("🚀 エンドポイント統合テスト開始")

    success = await test_multiagent_chat_endpoint()

    if success:
        logger.info("🎉 エンドポイント統合テストが成功しました！")
        return 0
    else:
        logger.error("❌ エンドポイント統合テストが失敗しました")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
