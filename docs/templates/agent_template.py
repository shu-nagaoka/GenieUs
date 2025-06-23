# Template for new Agent implementation
# 🚨 Claude Code: このテンプレートに従って実装してください
# 📋 必須参照: docs/guides/new-agent-creation.md

# 1. Import文（必ずファイル先頭に配置）
import logging
from typing import Dict, Any, Optional
from google.adk import Agent
from google.adk.tools import FunctionTool

# 2. エージェント作成関数（型アノテーション必須）
# 🚨 必須: ロガーDI注入パターン
def create_{domain}_agent(
    {domain}_tool: FunctionTool,
    logger: logging.Logger  # 🚨 必須: ロガーDI注入
) -> Agent:
    """{Domain}専門エージェント作成（ロガーDI統合版）
    
    Args:
        {domain}_tool: {Domain}専用FunctionTool
        logger: ログ出力用（DIコンテナから注入）
        
    Returns:
        Agent: 作成されたエージェント
        
    Raises:
        ValueError: ツールが無効な場合
    """
    logger.info("{Domain}専門エージェント作成開始")
    
    try:
        # ADK制約に従ったエージェント作成
        agent = Agent(
            model="gemini-2.5-flash-preview-05-20",
            name="{Domain}Specialist",
            instruction=create_{domain}_instruction(),
            tools=[{domain}_tool],
        )
        
        logger.info("{Domain}専門エージェント作成完了")
        return agent
        
    except Exception as e:
        logger.error(f"{Domain}エージェント作成エラー: {e}")
        raise

# 4. 指示文作成（ドメイン固有の実装）
def create_{domain}_instruction() -> str:
    """{Domain}専門エージェント用指示文"""
    return """
    あなたは{domain}に特化した専門家です。
    
    専門領域:
    - {専門領域1}
    - {専門領域2}
    - {専門領域3}
    
    対応方針:
    1. 安全性を最優先とした提案
    2. 年齢・状況を考慮したアドバイス
    3. 緊急性がある場合は医療機関への相談を推奨
    
    常に優しく、実践的なアドバイスを提供してください。
    """

# 🚨 Claude Code チェックポイント:
# □ Import文がファイル先頭に配置されている
# □ 型アノテーションが完備されている  
# □ エラーハンドリングが実装されている
# □ **ロガーDI注入が実装されている**（個別初期化禁止）
# □ **AgentManager統合が計画されている**（個別エージェント初期化禁止）
# □ ADK制約が遵守されている

# 📋 AgentManager統合例:
# class AgentManager:
#     def _initialize_{domain}_agent(self) -> None:
#         try:
#             {domain}_tool = self.container.{domain}_consultation_tool()
#             agent = create_{domain}_agent({domain}_tool, self.logger)
#             self._agents["{domain}"] = agent
#             self.logger.info("{Domain}エージェント初期化完了")
#         except Exception as e:
#             self.logger.error(f"{Domain}エージェント初期化エラー: {e}")
#             raise