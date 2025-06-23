#!/usr/bin/env python3
"""MVPコア機能の簡易テストスクリプト"""

import sys
from pathlib import Path

# プロジェクトルートを追加
sys.path.append(str(Path(__file__).parent.parent / "src"))

from src.di_provider.factory import get_container
from src.share.logger import setup_logger

logger = setup_logger(__name__)


def test_di_container():
    """DIコンテナーの動作確認"""
    logger.info("=== DIコンテナーテスト開始 ===")

    try:
        container = get_container()
        logger.info("✅ DIコンテナー取得成功")

        # AgentManagerの取得テスト
        agent_manager = container.agent_manager()
        logger.info("✅ AgentManager取得成功")

        # ツールの取得テスト
        tool = container.childcare_consultation_tool()
        logger.info("✅ ChildcareConsultationTool取得成功")

        return True

    except Exception as e:
        logger.error(f"❌ DIコンテナーテストエラー: {e}")
        return False


def test_agent_manager():
    """AgentManagerの統合テスト"""
    logger.info("=== AgentManager統合テスト開始 ===")

    try:
        container = get_container()
        agent_manager = container.agent_manager()

        # AgentManagerの初期化
        agent_manager.initialize_all_agents()
        logger.info("✅ AgentManager初期化成功")

        # エージェント取得テスト
        childcare_agent = agent_manager.get_agent("childcare")
        logger.info(f"✅ 子育てエージェント取得成功: {childcare_agent.name}")

        return True

    except Exception as e:
        logger.error(f"❌ AgentManager統合テストエラー: {e}")
        return False


def test_tool_function():
    """ツール関数の直接テスト"""
    logger.info("=== ツール関数テスト開始 ===")

    try:
        # DIコンテナーからツールを取得
        container = get_container()
        tool = container.childcare_consultation_tool()

        # ツール関数実行 - FunctionToolのfuncを直接呼び出し
        result = tool.func(
            message="夜泣きで困っています。生後3ヶ月です。",
            user_id="test_user",
            session_id="test_session",
            child_age_months=3,
        )

        if result["success"]:
            logger.info("✅ ツール関数実行成功")
            logger.info(f"レスポンス: {result['response'][:100]}...")
            return True
        else:
            logger.error(f"❌ ツール関数実行失敗: {result}")
            return False

    except Exception as e:
        logger.error(f"❌ ツール関数テストエラー: {e}")
        return False


def test_config_based_agent_creation():
    """設定ベースエージェント作成テスト"""
    logger.info("=== 設定ベースエージェント作成テスト開始 ===")

    try:
        container = get_container()
        agent_factory = container.agent_factory()

        # プリセット設定を使用してエージェント作成
        from src.agents.config.presets import AgentConfigPresets

        config = AgentConfigPresets.standard_childcare()
        agent = agent_factory.create_agent(config)

        logger.info("✅ 設定ベースエージェント作成成功")
        logger.info(f"エージェント名: {agent.name}")
        logger.info(f"エージェント設定: {config.agent_type}")
        return True

    except Exception as e:
        logger.error(f"❌ 設定ベースエージェント作成エラー: {e}")
        return False


def main():
    """メインテスト実行"""
    logger.info("🚀 MVPコア機能テスト開始")

    results = [
        test_di_container(),
        test_agent_manager(),
        test_tool_function(),
        test_config_based_agent_creation(),
    ]

    success_count = sum(results)
    total_count = len(results)

    logger.info(f"🎯 テスト結果: {success_count}/{total_count} 成功")

    if success_count == total_count:
        logger.info("🎉 MVPコア機能は正常に動作しています！")
        return 0
    else:
        logger.error("❌ 一部テストが失敗しました")
        return 1


if __name__ == "__main__":
    sys.exit(main())
