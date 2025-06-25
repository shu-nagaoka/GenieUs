"""Domain entities for GenieUs v2.0
子供記録・予測・努力分析のドメインエンティティ
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Literal, List, Optional, Dict


class EventType(str, Enum):
    """イベントタイプ列挙"""

    SLEEP = "sleep"
    FEEDING = "feeding"
    MOOD = "mood"
    MILESTONE = "milestone"
    PHOTO = "photo"
    HEALTH = "health"
    ACTIVITY = "activity"


class PredictionType(str, Enum):
    """予測タイプ列挙"""

    MOOD = "mood"
    SLEEP_PATTERN = "sleep_pattern"
    FEEDING_NEEDS = "feeding_needs"
    HEALTH_CONCERN = "health_concern"
    MILESTONE_READINESS = "milestone_readiness"


@dataclass
class ChildRecord:
    """子供の記録エンティティ"""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    child_id: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    event_type: EventType = EventType.MOOD
    value: float | None = None
    unit: str | None = None
    text_data: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0  # AI解析の信頼度 (0.0-1.0)
    source: str = "manual"  # "manual", "voice", "image", "ai_inference"
    parent_id: str | None = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """バリデーション"""
        if not self.child_id:
            raise ValueError("child_id is required")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")

        # デフォルト値設定
        if isinstance(self.event_type, str):
            self.event_type = EventType(self.event_type)

    @classmethod
    def create_sleep_record(
        cls,
        child_id: str,
        duration_minutes: float | None = None,
        quality: str | None = None,
        timestamp: datetime | None = None,
    ) -> "ChildRecord":
        """睡眠記録作成"""
        return cls(
            child_id=child_id,
            event_type=EventType.SLEEP,
            value=duration_minutes,
            unit="minutes",
            text_data=quality,
            timestamp=timestamp or datetime.now(),
            metadata={"quality": quality} if quality else {},
        )

    @classmethod
    def create_feeding_record(
        cls,
        child_id: str,
        amount_ml: float | None = None,
        food_type: str | None = None,
        timestamp: datetime | None = None,
    ) -> "ChildRecord":
        """授乳・食事記録作成"""
        return cls(
            child_id=child_id,
            event_type=EventType.FEEDING,
            value=amount_ml,
            unit="ml",
            text_data=food_type,
            timestamp=timestamp or datetime.now(),
            metadata={"food_type": food_type} if food_type else {},
        )

    @classmethod
    def create_mood_record(
        cls,
        child_id: str,
        mood_score: float | None = None,
        mood_description: str | None = None,
        timestamp: datetime | None = None,
    ) -> "ChildRecord":
        """機嫌記録作成"""
        return cls(
            child_id=child_id,
            event_type=EventType.MOOD,
            value=mood_score,
            unit="score",
            text_data=mood_description,
            timestamp=timestamp or datetime.now(),
            metadata={"mood": mood_description} if mood_description else {},
        )

    def to_dict(self) -> dict[str, Any]:
        """辞書形式に変換"""
        return {
            "id": self.id,
            "child_id": self.child_id,
            "timestamp": self.timestamp.isoformat(),
            "event_type": self.event_type.value,
            "value": self.value,
            "unit": self.unit,
            "text_data": self.text_data,
            "metadata": self.metadata,
            "confidence": self.confidence,
            "source": self.source,
            "parent_id": self.parent_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


@dataclass
class Child:
    """子供エンティティ"""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    birth_date: datetime = field(default_factory=datetime.now)
    parent_ids: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """バリデーション"""
        if not self.name.strip():
            raise ValueError("name is required")

    @property
    def age_in_months(self) -> int:
        """月齢計算"""
        now = datetime.now()
        months = (now.year - self.birth_date.year) * 12 + (now.month - self.birth_date.month)
        return max(0, months)

    @property
    def age_in_days(self) -> int:
        """日齢計算"""
        now = datetime.now()
        return max(0, (now - self.birth_date).days)

    def to_dict(self) -> dict[str, Any]:
        """辞書形式に変換"""
        return {
            "id": self.id,
            "name": self.name,
            "birth_date": self.birth_date.isoformat(),
            "parent_ids": self.parent_ids,
            "metadata": self.metadata,
            "age_months": self.age_in_months,
            "age_days": self.age_in_days,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


@dataclass
class PredictionResult:
    """予測結果エンティティ"""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    child_id: str = ""
    prediction_date: datetime = field(default_factory=datetime.now)
    prediction_type: PredictionType = PredictionType.MOOD
    prediction: str = ""
    confidence: float = 0.0
    reasoning: str = ""
    suggested_actions: list[str] = field(default_factory=list)
    risk_factors: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """バリデーション"""
        if not self.child_id:
            raise ValueError("child_id is required")
        if not self.prediction.strip():
            raise ValueError("prediction is required")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")

        if isinstance(self.prediction_type, str):
            self.prediction_type = PredictionType(self.prediction_type)

    @classmethod
    def create_daily_mood_prediction(
        cls,
        child_id: str,
        prediction: str,
        confidence: float,
        reasoning: str,
        suggested_actions: list[str],
    ) -> "PredictionResult":
        """デイリー機嫌予測作成"""
        return cls(
            child_id=child_id,
            prediction_type=PredictionType.MOOD,
            prediction=prediction,
            confidence=confidence,
            reasoning=reasoning,
            suggested_actions=suggested_actions,
        )

    def to_dict(self) -> dict[str, Any]:
        """辞書形式に変換"""
        return {
            "id": self.id,
            "child_id": self.child_id,
            "prediction_date": self.prediction_date.isoformat(),
            "prediction_type": self.prediction_type.value,
            "prediction": self.prediction,
            "confidence": self.confidence,
            "reasoning": self.reasoning,
            "suggested_actions": self.suggested_actions,
            "risk_factors": self.risk_factors,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class EffortMetric:
    """努力指標エンティティ"""

    metric_name: str = ""
    value: float = 0.0
    unit: str = ""
    comparison: str = ""  # "先週比+40%" など
    impact: str = ""  # "子供の笑顔が25%増加" など

    def to_dict(self) -> dict[str, Any]:
        return {
            "metric": self.metric_name,
            "value": self.value,
            "unit": self.unit,
            "comparison": self.comparison,
            "impact": self.impact,
        }


@dataclass
class EffortReport:
    """親の努力レポートエンティティ"""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    parent_id: str = ""
    child_id: str = ""
    period_start: datetime = field(default_factory=datetime.now)
    period_end: datetime = field(default_factory=datetime.now)
    achievements: list[EffortMetric] = field(default_factory=list)
    growth_evidence: list[str] = field(default_factory=list)
    affirmation_message: str = ""
    overall_score: float = 0.0  # 0.0-1.0
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """バリデーション"""
        if not self.parent_id:
            raise ValueError("parent_id is required")
        if not self.child_id:
            raise ValueError("child_id is required")
        if not 0.0 <= self.overall_score <= 1.0:
            raise ValueError("overall_score must be between 0.0 and 1.0")

    @classmethod
    def create_weekly_report(
        cls,
        parent_id: str,
        child_id: str,
        achievements: list[EffortMetric],
        growth_evidence: list[str],
        affirmation_message: str,
    ) -> "EffortReport":
        """週次レポート作成"""
        now = datetime.now()
        period_start = now - timedelta(days=7)

        return cls(
            parent_id=parent_id,
            child_id=child_id,
            period_start=period_start,
            period_end=now,
            achievements=achievements,
            growth_evidence=growth_evidence,
            affirmation_message=affirmation_message,
            overall_score=0.8,  # デフォルト高評価
        )

    @property
    def period_days(self) -> int:
        """期間日数"""
        return (self.period_end - self.period_start).days

    def add_achievement(self, metric: EffortMetric):
        """実績追加"""
        self.achievements.append(metric)

    def add_growth_evidence(self, evidence: str):
        """成長の証拠追加"""
        self.growth_evidence.append(evidence)

    def to_dict(self) -> dict[str, Any]:
        """辞書形式に変換"""
        return {
            "id": self.id,
            "parent_id": self.parent_id,
            "child_id": self.child_id,
            "period_start": self.period_start.isoformat(),
            "period_end": self.period_end.isoformat(),
            "period_days": self.period_days,
            "achievements": [achievement.to_dict() for achievement in self.achievements],
            "growth_evidence": self.growth_evidence,
            "affirmation_message": self.affirmation_message,
            "overall_score": self.overall_score,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class VoiceRecordingData:
    """音声記録データエンティティ"""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    raw_text: str = ""
    processed_events: list[ChildRecord] = field(default_factory=list)
    confidence: float = 0.0
    processing_status: Literal["pending", "processing", "completed", "failed"] = "pending"
    error_message: str | None = None
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "raw_text": self.raw_text,
            "processed_events": [event.to_dict() for event in self.processed_events],
            "confidence": self.confidence,
            "processing_status": self.processing_status,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class ImageRecordingData:
    """画像記録データエンティティ"""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    image_path: str = ""
    detected_items: list[str] = field(default_factory=list)
    estimated_data: dict[str, Any] = field(default_factory=dict)
    emotion_detected: str | None = None
    confidence: float = 0.0
    suggestions: list[str] = field(default_factory=list)
    processing_status: Literal["pending", "processing", "completed", "failed"] = "pending"
    error_message: str | None = None
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "image_path": self.image_path,
            "detected_items": self.detected_items,
            "estimated_data": self.estimated_data,
            "emotion_detected": self.emotion_detected,
            "confidence": self.confidence,
            "suggestions": self.suggestions,
            "processing_status": self.processing_status,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class GrowthRecord:
    """成長記録エンティティ"""

    record_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    child_id: Optional[str] = None
    child_name: str = ""
    date: str = ""
    age_in_months: int = 0
    type: str = ""
    category: str = ""
    title: str = ""
    description: str = ""
    value: Optional[str] = None
    unit: Optional[str] = None
    image_url: Optional[str] = None
    detected_by: str = "parent"
    confidence: Optional[float] = None
    emotions: Optional[List[str]] = None
    development_stage: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    def __post_init__(self):
        """バリデーション"""
        if not self.user_id.strip():
            raise ValueError("user_id is required")
        if not self.child_name.strip():
            raise ValueError("child_name is required")
        if not self.title.strip():
            raise ValueError("title is required")

    @classmethod
    def from_dict(cls, user_id: str, record_data: dict) -> "GrowthRecord":
        """辞書データから成長記録エンティティを作成"""
        now = datetime.now().isoformat()
        return cls(
            record_id=record_data.get("id", str(uuid.uuid4())),
            user_id=user_id,
            child_id=record_data.get("child_id"),
            child_name=record_data.get("child_name", ""),
            date=record_data.get("date", ""),
            age_in_months=record_data.get("age_in_months", 0),
            type=record_data.get("type", ""),
            category=record_data.get("category", ""),
            title=record_data.get("title", ""),
            description=record_data.get("description", ""),
            value=record_data.get("value"),
            unit=record_data.get("unit"),
            image_url=record_data.get("image_url"),
            detected_by=record_data.get("detected_by", "parent"),
            confidence=record_data.get("confidence"),
            emotions=record_data.get("emotions"),
            development_stage=record_data.get("development_stage"),
            created_at=record_data.get("created_at", now),
            updated_at=record_data.get("updated_at", now),
        )

    def to_dict(self) -> dict[str, Any]:
        """辞書形式に変換"""
        return {
            "id": self.record_id,
            "user_id": self.user_id,
            "child_id": self.child_id,
            "child_name": self.child_name,
            "date": self.date,
            "age_in_months": self.age_in_months,
            "type": self.type,
            "category": self.category,
            "title": self.title,
            "description": self.description,
            "value": self.value,
            "unit": self.unit,
            "image_url": self.image_url,
            "detected_by": self.detected_by,
            "confidence": self.confidence,
            "emotions": self.emotions,
            "development_stage": self.development_stage,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


@dataclass
class MemoryRecord:
    """メモリー記録エンティティ"""

    memory_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    title: str = ""
    description: str = ""
    date: str = ""
    type: str = ""  # photo, video, album
    category: str = ""  # milestone, daily, family, special
    media_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    location: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    favorited: bool = False
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    def __post_init__(self):
        """バリデーション"""
        if not self.user_id.strip():
            raise ValueError("user_id is required")
        if not self.title.strip():
            raise ValueError("title is required")

    @classmethod
    def from_dict(cls, user_id: str, memory_data: dict) -> "MemoryRecord":
        """辞書データからメモリー記録エンティティを作成"""
        now = datetime.now().isoformat()
        return cls(
            memory_id=memory_data.get("id", str(uuid.uuid4())),
            user_id=user_id,
            title=memory_data.get("title", ""),
            description=memory_data.get("description", ""),
            date=memory_data.get("date", ""),
            type=memory_data.get("type", ""),
            category=memory_data.get("category", ""),
            media_url=memory_data.get("media_url"),
            thumbnail_url=memory_data.get("thumbnail_url"),
            location=memory_data.get("location"),
            tags=memory_data.get("tags", []),
            favorited=memory_data.get("favorited", False),
            created_at=memory_data.get("created_at", now),
            updated_at=memory_data.get("updated_at", now),
        )

    def to_dict(self) -> dict[str, Any]:
        """辞書形式に変換"""
        return {
            "id": self.memory_id,
            "user_id": self.user_id,
            "title": self.title,
            "description": self.description,
            "date": self.date,
            "type": self.type,
            "category": self.category,
            "media_url": self.media_url,
            "thumbnail_url": self.thumbnail_url,
            "location": self.location,
            "tags": self.tags,
            "favorited": self.favorited,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


@dataclass
class ScheduleEvent:
    """予定イベントエンティティ"""

    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    title: str = ""
    date: str = ""
    time: str = ""
    type: str = ""  # vaccination, outing, checkup, other
    location: Optional[str] = None
    description: Optional[str] = None
    status: str = "upcoming"  # upcoming, completed, cancelled
    created_by: str = "genie"
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    def __post_init__(self):
        """バリデーション"""
        if not self.user_id.strip():
            raise ValueError("user_id is required")
        if not self.title.strip():
            raise ValueError("title is required")

    @classmethod
    def from_dict(cls, user_id: str, event_data: dict) -> "ScheduleEvent":
        """辞書データから予定イベントエンティティを作成"""
        now = datetime.now().isoformat()
        return cls(
            event_id=event_data.get("id", str(uuid.uuid4())),
            user_id=user_id,
            title=event_data.get("title", ""),
            date=event_data.get("date", ""),
            time=event_data.get("time", ""),
            type=event_data.get("type", ""),
            location=event_data.get("location"),
            description=event_data.get("description"),
            status=event_data.get("status", "upcoming"),
            created_by=event_data.get("created_by", "genie"),
            created_at=event_data.get("created_at", now),
            updated_at=event_data.get("updated_at", now),
        )

    def to_dict(self) -> dict[str, Any]:
        """辞書形式に変換"""
        return {
            "id": self.event_id,
            "user_id": self.user_id,
            "title": self.title,
            "date": self.date,
            "time": self.time,
            "type": self.type,
            "location": self.location,
            "description": self.description,
            "status": self.status,
            "created_by": self.created_by,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


@dataclass
class EffortReportRecord:
    """努力レポートエンティティ"""

    report_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    period_days: int = 7
    effort_count: int = 0
    score: float = 0.0
    highlights: List[str] = field(default_factory=list)
    categories: Dict[str, int] = field(default_factory=dict)
    summary: str = ""
    achievements: List[str] = field(default_factory=list)
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    def __post_init__(self):
        """バリデーション"""
        if not self.user_id.strip():
            raise ValueError("user_id is required")
        if not 0.0 <= self.score <= 100.0:
            raise ValueError("score must be between 0.0 and 100.0")

    @classmethod
    def from_dict(cls, user_id: str, report_data: dict) -> "EffortReportRecord":
        """辞書データから努力レポートエンティティを作成"""
        now = datetime.now().isoformat()
        return cls(
            report_id=report_data.get("id", str(uuid.uuid4())),
            user_id=user_id,
            period_days=report_data.get("period_days", 7),
            effort_count=report_data.get("effort_count", 0),
            score=report_data.get("score", 0.0),
            highlights=report_data.get("highlights", []),
            categories=report_data.get("categories", {}),
            summary=report_data.get("summary", ""),
            achievements=report_data.get("achievements", []),
            created_at=report_data.get("created_at", now),
            updated_at=report_data.get("updated_at", now),
        )

    def to_dict(self) -> dict[str, Any]:
        """辞書形式に変換"""
        return {
            "id": self.report_id,
            "user_id": self.user_id,
            "period_days": self.period_days,
            "effort_count": self.effort_count,
            "score": self.score,
            "highlights": self.highlights,
            "categories": self.categories,
            "summary": self.summary,
            "achievements": self.achievements,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


@dataclass
class FamilyInfo:
    """家族情報エンティティ"""

    family_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    parent_name: str = ""
    family_structure: str = ""
    concerns: str = ""
    children: list[dict] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """バリデーション"""
        if not self.user_id.strip():
            raise ValueError("user_id is required")

    @classmethod
    def from_dict(cls, user_id: str, family_data: dict) -> "FamilyInfo":
        """辞書データから家族情報エンティティを作成"""
        return cls(
            user_id=user_id,
            parent_name=family_data.get("parent_name", ""),
            family_structure=family_data.get("family_structure", ""),
            concerns=family_data.get("concerns", ""),
            children=family_data.get("children", []),
        )

    def to_dict(self) -> dict[str, Any]:
        """辞書形式に変換"""
        return {
            "family_id": self.family_id,
            "user_id": self.user_id,
            "parent_name": self.parent_name,
            "family_structure": self.family_structure,
            "concerns": self.concerns,
            "children": self.children,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
