from dataclasses import dataclass


@dataclass
class SafetyAssessmentResult:
    """安全性評価の結果"""

    urgency: str
    reason: str
    recommended_action: str
    risk_factors: list[str]


@dataclass
class AgeDetectionResult:
    """年齢検出の結果"""

    age_group: str
    estimated_age: str
    developmental_stage: str
    confidence: float


@dataclass
class ChildcareAdviseResult:
    """子育てアドバイスの結果"""

    advice: str
    detailed_advice: str
    urgency_level: str
    reason: str
    risk_factors: list
    follow_up: list


@dataclass
class DevelopmentAssessmentResult:
    """発育評価の結果"""

    development_status: str
    milestone_assessment: str
    concerns: list[str]
    recommendations: list[str]
    next_checkpoints: list[str]
    urgency_level: str


# 削除されたProtocol一覧:
# - SafetyAssessorProtocol (Agent内で処理)
# - AgeDetectorProtocol (Agent内で処理)
# - ChildcareAdviserProtocol (Agent内で処理)
# - DevelopmentAdviserProtocol (Agent内で処理)
#
# Agent中心アーキテクチャでは、これらの判断・アドバイス生成は
# すべてGemini-poweredなAgentが担当するため、
# 個別のProtocolは不要となりました。
