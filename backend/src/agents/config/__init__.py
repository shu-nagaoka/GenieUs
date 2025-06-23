"""エージェント設定パッケージ - 設定ベース設計の基盤

このパッケージは、エージェントの作成と管理を設定ベースで行うための
基盤クラスを提供します。

主要コンポーネント:
- AgentConfig: エージェントの設定定義
- ToolRegistry: ツールの一元管理
- AgentFactory: 設定ベースエージェント作成
- AgentConfigPresets: よく使用される設定のプリセット

使用例:
    from src.agents.config import AgentConfigPresets, AgentFactory, ToolRegistry

    # プリセット使用
    config = AgentConfigPresets.standard_childcare()

    # ファクトリーでエージェント作成
    factory = AgentFactory(tool_registry, logger)
    agent = factory.create_agent(config)
"""

from src.agents.config.agent_config import AgentConfig
from src.agents.config.tool_registry import ToolRegistry
from src.agents.config.agent_factory import AgentFactory
from src.agents.config.presets import AgentConfigPresets

__all__ = ["AgentConfig", "ToolRegistry", "AgentFactory", "AgentConfigPresets"]
