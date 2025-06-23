#!/usr/bin/env python3
"""main.py経由の統合テストスクリプト
新しいDIアーキテクチャでの動作確認
"""

import asyncio
import sys

sys.path.append("src")

from src.di_provider.factory import get_container
from src.presentation.api.routes.multiagent_chat import MultiAgentChatMessage
from src.share.logger import setup_logger

logger = setup_logger(__name__)


async def test_main_integration():
    """main.pyと同じ手順でのDI統合テスト"""
    logger.info("=== main.py統合テスト開始 ===")

    try:
        # Step 1: DIコンテナの初期化（main.pyと同じ）
        container = get_container()
        logger.info("✅ DIコンテナー初期化完了")

        # Step 2: AgentManagerによる統一管理（main.pyと同じ）
        agent_manager = container.agent_manager()
        agent_manager.initialize_all_agents()
        logger.info("✅ AgentManager初期化完了")

        # Step 3: マルチエージェント統合テスト
        test_message = MultiAgentChatMessage(
            message="夜泣きで困っています。生後3ヶ月です。",
            user_id="test_user_main",
            session_id="test_session_main_001",
            requested_agent="childcare",
        )

        logger.info("マルチエージェントチャット実行開始")
        # AgentManagerのroute_queryを直接テスト（シンプルな文字列レスポンス）
        response_text = await agent_manager.route_query_async(
            test_message.message, test_message.user_id, test_message.session_id
        )

        # 結果確認
        logger.info("✅ main.py統合テスト成功")
        logger.info(f"レスポンス: {response_text[:100]}...")
        logger.info(f"レスポンス長: {len(response_text)} 文字")

        return True

    except Exception as e:
        logger.error(f"❌ main.py統合テストエラー: {e}")
        import traceback

        logger.error(f"詳細: {traceback.format_exc()}")
        return False


async def test_component_isolation():
    """コンポーネント分離テスト"""
    logger.info("=== コンポーネント分離テスト開始 ===")

    try:
        # 各コンポーネントが独立して動作することを確認

        # 1. DIコンテナ単体テスト
        container = get_container()
        tool = container.childcare_consultation_tool()
        logger.info("✅ DIコンテナ単体動作確認")

        # 2. AgentManager単体テスト
        agent_manager = container.agent_manager()
        agent_manager.initialize_all_agents()
        logger.info("✅ AgentManager単体動作確認完了")

        # 3. ツール単体テスト
        tool_result = tool.func(
            message="テストメッセージ",
            user_id="test_user",
            session_id="test_session",
        )
        logger.info(f"✅ ツール単体動作確認: {tool_result['success']}")

        return True

    except Exception as e:
        logger.error(f"❌ コンポーネント分離テストエラー: {e}")
        return False


async def main():
    """メインテスト実行"""
    logger.info("🚀 main.py統合テスト開始")

    results = [
        await test_main_integration(),
        await test_component_isolation(),
    ]

    success_count = sum(results)
    total_count = len(results)

    logger.info(f"🎯 テスト結果: {success_count}/{total_count} 成功")

    if success_count == total_count:
        logger.info("🎉 main.py統合テストが全て成功しました！")
        logger.info("新しいDIアーキテクチャが正常に動作しています")
        return 0
    else:
        logger.error("❌ 一部テストが失敗しました")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
