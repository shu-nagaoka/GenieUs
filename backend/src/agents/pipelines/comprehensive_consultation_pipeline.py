import logging

from google.adk.agents import Agent, ParallelAgent, SequentialAgent

from src.agents.individual.synthesis_agent import create_synthesis_agent
from src.agents.individual.triage_agent import create_triage_agent


def create_comprehensive_consultation_pipeline(
    childcare_agent: Agent,
    development_agent: Agent,
    logger: logging.Logger,
    sleep_agent: Agent | None = None,
    nutrition_agent: Agent | None = None,
) -> Agent:
    """統合相談パイプライン作成

    マルチエージェントによる包括的な子育て相談システム

    Args:
        childcare_agent: 子育て一般相談エージェント
        development_agent: 発育・発達相談エージェント
        logger: ロガー（DIコンテナから注入）
        sleep_agent: 睡眠相談エージェント（オプション）
        nutrition_agent: 栄養相談エージェント（オプション）

    Returns:
        Agent: 統合相談パイプライン

    """
    logger.info("統合相談パイプライン作成開始")

    try:
        # 1. トリアージエージェント（緊急度・専門分野判定）
        triage_agent = create_triage_agent(logger)

        # 2. 専門家エージェント並列実行
        expert_agents = [childcare_agent, development_agent]

        # オプションエージェントが利用可能な場合は追加
        if sleep_agent:
            expert_agents.append(sleep_agent)
        if nutrition_agent:
            expert_agents.append(nutrition_agent)

        parallel_experts = ParallelAgent(
            name="ParallelExpertConsultation",
            description="複数専門家による並列相談",
            sub_agents=expert_agents,
        )

        # 3. 統合エージェント（結果統合・総合アドバイス生成）
        synthesis_agent = create_synthesis_agent(logger)

        # 4. 統合パイプライン（Sequential実行）
        comprehensive_pipeline = SequentialAgent(
            name="ComprehensiveConsultationPipeline",
            description="包括的子育て相談パイプライン",
            sub_agents=[
                triage_agent,  # Step 1: 緊急度・専門分野判定
                parallel_experts,  # Step 2: 複数専門家による並列相談
                synthesis_agent,  # Step 3: 結果統合・総合アドバイス
            ],
        )

        logger.info(
            f"統合相談パイプライン作成完了: 専門家数={len(expert_agents)}名, パイプライン段階=3段階",
        )

        return comprehensive_pipeline

    except Exception as e:
        logger.error(f"統合相談パイプライン作成エラー: {e}")
        raise


def create_emergency_consultation_pipeline(
    childcare_agent: Agent,
    development_agent: Agent,
    logger: logging.Logger,
) -> Agent:
    """緊急相談パイプライン作成

    緊急度の高い相談に特化した迅速対応パイプライン

    Args:
        childcare_agent: 子育て一般相談エージェント
        development_agent: 発育・発達相談エージェント
        logger: ロガー（DIコンテナから注入）

    Returns:
        Agent: 緊急相談パイプライン

    """
    logger.info("緊急相談パイプライン作成開始")

    try:
        # 緊急時は迅速性を優先し、シンプルな構成
        # トリアージ → 主要専門家による並列相談のみ

        triage_agent = create_triage_agent(logger)

        # 緊急時は主要2専門家のみで迅速対応
        emergency_experts = ParallelAgent(
            name="EmergencyExpertConsultation",
            description="緊急時専門家相談（迅速対応）",
            sub_agents=[childcare_agent, development_agent],
        )

        emergency_pipeline = SequentialAgent(
            name="EmergencyConsultationPipeline",
            description="緊急相談パイプライン（迅速対応特化）",
            sub_agents=[
                triage_agent,  # Step 1: 緊急度判定
                emergency_experts,  # Step 2: 主要専門家による迅速相談
            ],
        )

        logger.info("緊急相談パイプライン作成完了")
        return emergency_pipeline

    except Exception as e:
        logger.error(f"緊急相談パイプライン作成エラー: {e}")
        raise


def get_pipeline_info() -> dict[str, str]:
    """利用可能なパイプライン情報を取得

    Returns:
        Dict[str, str]: パイプライン名と説明の辞書

    """
    return {
        "comprehensive": "包括的相談パイプライン - 全専門家による詳細な相談",
        "emergency": "緊急相談パイプライン - 迅速対応に特化した相談",
    }
