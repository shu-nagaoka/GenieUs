#!/usr/bin/env python3
"""ADK標準ルーティングシステムのテストスクリプト

新しいADK標準パターンによるルーティングコーディネーターの動作を検証
"""

import os
import sys

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from google.adk.agents import LlmAgent

from src.agents.adk_routing_coordinator import AdkRoutingCoordinator
from src.agents.adk_routing_strategy_adapter import AdkRoutingStrategyAdapter
from src.share.logger import setup_logger


def create_mock_specialist_agents():
    """モック専門エージェントを作成"""
    specialists = {}

    specialist_configs = {
        "nutrition_specialist": "食事・栄養の専門家",
        "sleep_specialist": "睡眠・夜泣きの専門家",
        "development_specialist": "発達・成長の専門家",
        "health_specialist": "健康・医療の専門家",
        "behavior_specialist": "行動・しつけの専門家",
    }

    for agent_name, description in specialist_configs.items():
        specialist = LlmAgent(
            name=agent_name,
            instruction=f"あなたは{description}です。専門的なアドバイスを提供してください。",
        )
        specialists[agent_name] = specialist

    return specialists


def test_adk_routing_coordinator():
    """ADKルーティングコーディネーターのテスト"""
    print("🎯 ADKルーティングコーディネーター テスト開始")

    # ロガー初期化
    logger = setup_logger("adk_routing_test")

    try:
        # モック専門エージェント作成
        specialist_agents = create_mock_specialist_agents()

        # ADKルーティングコーディネーター作成
        coordinator = AdkRoutingCoordinator(specialist_agents=specialist_agents, logger=logger)

        print(f"✅ コーディネーター作成成功: {len(specialist_agents)}専門エージェント")

        # 統計情報表示
        stats = coordinator.get_routing_statistics()
        print(f"📊 統計情報: {stats}")

        # コーディネーターエージェント取得
        coord_agent = coordinator.get_coordinator_agent()
        print(f"🤖 コーディネーターエージェント: {coord_agent.name}")

        return coordinator

    except Exception as e:
        print(f"❌ コーディネーター作成失敗: {e}")
        raise


def test_adk_routing_adapter():
    """ADKルーティング戦略アダプターのテスト"""
    print("\n🔄 ADKルーティング戦略アダプター テスト開始")

    logger = setup_logger("adk_adapter_test")

    try:
        # コーディネーター作成
        specialist_agents = create_mock_specialist_agents()
        coordinator = AdkRoutingCoordinator(specialist_agents=specialist_agents, logger=logger)

        # アダプター作成
        adapter = AdkRoutingStrategyAdapter(adk_coordinator=coordinator, logger=logger)

        print(f"✅ アダプター作成成功: {adapter.get_strategy_name()}")

        # テストクエリ
        test_queries = [
            "夜泣きがひどくて困っています",
            "食事を食べてくれません",
            "発達が気になります",
            "熱が出ています",
        ]

        for query in test_queries:
            agent_id, routing_info = adapter.determine_agent(query)
            print(f"🎯 '{query[:20]}...' → {agent_id} (信頼度: {routing_info['confidence']})")

        return adapter

    except Exception as e:
        print(f"❌ アダプターテスト失敗: {e}")
        raise


def test_error_handling():
    """エラーハンドリングのテスト"""
    print("\n🛡️ エラーハンドリング テスト開始")

    logger = setup_logger("error_test")

    try:
        # 空の専門エージェントでテスト
        try:
            AdkRoutingCoordinator(specialist_agents={}, logger=logger)
            print("❌ 空エージェント検証失敗")
        except ValueError as e:
            print(f"✅ 空エージェント検証成功: {e}")

        # Noneロガーでテスト
        try:
            AdkRoutingCoordinator(specialist_agents={"test": LlmAgent(name="test")}, logger=None)
            print("❌ Noneロガー検証失敗")
        except TypeError as e:
            print(f"✅ Noneロガー検証成功: {e}")

        print("✅ エラーハンドリングテスト完了")

    except Exception as e:
        print(f"❌ エラーハンドリングテスト失敗: {e}")


def main():
    """メインテスト関数"""
    print("🚀 ADK標準ルーティングシステム 総合テスト")
    print("=" * 60)

    try:
        # 基本機能テスト
        coordinator = test_adk_routing_coordinator()
        adapter = test_adk_routing_adapter()

        # エラーハンドリングテスト
        test_error_handling()

        print("\n" + "=" * 60)
        print("🎉 全テスト完了!")
        print(f"✅ コーディネーター戦略: {coordinator.get_routing_strategy_name()}")
        print(f"✅ アダプター戦略: {adapter.get_strategy_name()}")
        print(f"✅ 利用可能専門家: {coordinator.get_available_specialists()}")

    except Exception as e:
        print(f"\n❌ テスト実行エラー: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
