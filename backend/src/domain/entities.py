"""Domain entities for GenieUs v2.0
子供記録・予測・努力分析のドメインエンティティ
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Literal


class EventType(str, Enum):
    """イベントタイプ列挙"""

    SLEEP = "sleep"
    FEEDING = "feeding"
    MOOD = "mood"
    MILESTONE = "milestone"
    PHOTO = "photo"
    HEALTH = "health"
    ACTIVITY = "activity"
    OTHER = "other"


class MealType(str, Enum):
    """食事タイプ列挙"""

    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    SNACK = "snack"


class FoodDetectionSource(str, Enum):
    """食事検出ソース列挙"""

    MANUAL = "manual"
    MANUAL_ENTRY = "manual_entry"
    IMAGE_AI = "image_ai"
    VOICE_AI = "voice_ai"
    IMPORT = "import"


class DifficultyLevel(str, Enum):
    """調理難易度列挙"""

    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class PlanCreatedBy(str, Enum):
    """プラン作成者列挙"""

    USER = "user"
    GENIE = "genie"


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
class MealRecord:
    """個別食事記録エンティティ"""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    child_id: str = ""
    meal_name: str = ""
    meal_type: MealType = MealType.SNACK
    detected_foods: list[str] = field(default_factory=list)
    nutrition_info: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    detection_source: FoodDetectionSource = FoodDetectionSource.MANUAL
    confidence: float = 1.0  # AI検出の信頼度 (0.0-1.0)
    image_path: str | None = None
    notes: str | None = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """バリデーション"""
        if not self.child_id:
            raise ValueError("child_id is required")
        if not self.meal_name.strip():
            raise ValueError("meal_name is required")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")

        # Enum変換
        if isinstance(self.meal_type, str):
            self.meal_type = MealType(self.meal_type)
        if isinstance(self.detection_source, str):
            self.detection_source = FoodDetectionSource(self.detection_source)

    @classmethod
    def create_from_ai_detection(
        cls,
        child_id: str,
        meal_name: str,
        detected_foods: list[str],
        nutrition_info: dict[str, Any],
        meal_type: MealType,
        confidence: float,
        image_path: str | None = None,
        timestamp: datetime | None = None,
    ) -> "MealRecord":
        """AI検出結果から食事記録作成"""
        return cls(
            child_id=child_id,
            meal_name=meal_name,
            meal_type=meal_type,
            detected_foods=detected_foods,
            nutrition_info=nutrition_info,
            detection_source=FoodDetectionSource.IMAGE_AI,
            confidence=confidence,
            image_path=image_path,
            timestamp=timestamp or datetime.now(),
        )

    @classmethod
    def create_manual_record(
        cls,
        child_id: str,
        meal_name: str,
        meal_type: MealType,
        detected_foods: list[str] | None = None,
        notes: str | None = None,
        timestamp: datetime | None = None,
    ) -> "MealRecord":
        """手動入力から食事記録作成"""
        return cls(
            child_id=child_id,
            meal_name=meal_name,
            meal_type=meal_type,
            detected_foods=detected_foods or [],
            detection_source=FoodDetectionSource.MANUAL,
            confidence=1.0,
            notes=notes,
            timestamp=timestamp or datetime.now(),
        )

    @classmethod
    def from_dict(cls, meal_data: dict) -> "MealRecord":
        """辞書データからMealRecordエンティティを作成"""
        from datetime import datetime as dt

        # timestampの処理 (meal_date, meal_timestamp, timestampのいずれかから取得)
        timestamp = None
        timestamp_str = meal_data.get("timestamp") or meal_data.get("meal_date") or meal_data.get("meal_timestamp")

        if timestamp_str:
            try:
                if isinstance(timestamp_str, str):
                    # ISO形式をパース
                    timestamp = dt.fromisoformat(timestamp_str.replace("Z", ""))
                elif isinstance(timestamp_str, dt):
                    timestamp = timestamp_str
            except Exception:
                # パースに失敗した場合は現在時刻
                timestamp = dt.now()
        else:
            timestamp = dt.now()

        # detection_sourceの処理 (analysis_source, detection_source のマッピング)
        detection_source_str = meal_data.get("detection_source") or meal_data.get("analysis_source", "manual")
        try:
            if detection_source_str == "image_ai" or detection_source_str == "ai":
                detection_source = FoodDetectionSource.IMAGE_AI
            elif detection_source_str == "manual":
                detection_source = FoodDetectionSource.MANUAL
            else:
                detection_source = FoodDetectionSource.MANUAL
        except Exception:
            detection_source = FoodDetectionSource.MANUAL

        # meal_typeの処理
        meal_type_str = meal_data.get("meal_type", "snack")
        try:
            meal_type = MealType(meal_type_str)
        except Exception:
            meal_type = MealType.SNACK

        # nutrition_infoの処理
        nutrition_info = meal_data.get("nutrition_info", {})
        if not isinstance(nutrition_info, dict):
            nutrition_info = {}

        now = dt.now()
        return cls(
            id=meal_data.get("id", str(uuid.uuid4())),
            child_id=meal_data.get("child_id", "default_child"),
            meal_name=meal_data.get("meal_name", "食事記録"),
            meal_type=meal_type,
            detected_foods=meal_data.get("detected_foods", []),
            nutrition_info=nutrition_info,
            timestamp=timestamp,
            detection_source=detection_source,
            confidence=float(meal_data.get("confidence", 1.0)),
            image_path=meal_data.get("image_path"),
            notes=meal_data.get("notes"),
            created_at=dt.fromisoformat(meal_data["created_at"]) if meal_data.get("created_at") else now,
            updated_at=dt.fromisoformat(meal_data["updated_at"]) if meal_data.get("updated_at") else now,
        )

    def to_dict(self) -> dict[str, Any]:
        """辞書形式に変換"""
        return {
            "id": self.id,
            "child_id": self.child_id,
            "meal_name": self.meal_name,
            "meal_type": self.meal_type.value,
            "detected_foods": self.detected_foods,
            "nutrition_info": self.nutrition_info,
            "timestamp": self.timestamp.isoformat(),
            "detection_source": self.detection_source.value,
            "confidence": self.confidence,
            "image_path": self.image_path,
            "notes": self.notes,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    def update_nutrition_info(self, nutrition_info: dict[str, Any]) -> None:
        """栄養情報を更新"""
        self.nutrition_info.update(nutrition_info)
        self.updated_at = datetime.now()

    def add_note(self, note: str) -> None:
        """メモを追加"""
        if self.notes:
            self.notes += f"\n{note}"
        else:
            self.notes = note
        self.updated_at = datetime.now()

    @property
    def is_ai_detected(self) -> bool:
        """AI検出による記録かどうか"""
        return self.detection_source in [FoodDetectionSource.IMAGE_AI, FoodDetectionSource.VOICE_AI]

    @property
    def total_nutrition_score(self) -> float:
        """栄養バランススコア計算"""
        if not self.nutrition_info:
            return 0.0

        balance_score = self.nutrition_info.get("balance_score", 0)
        if isinstance(balance_score, (int, float)):
            return float(balance_score)
        return 0.0


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
    child_id: str | None = None
    child_name: str = ""
    date: str = ""
    age_in_months: int = 0
    type: str = ""
    category: str = ""
    title: str = ""
    description: str = ""
    value: str | None = None
    unit: str | None = None
    image_url: str | None = None
    detected_by: str = "parent"
    confidence: float | None = None
    emotions: list[str] | None = None
    development_stage: str | None = None
    created_at: str | None = None
    updated_at: str | None = None

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
    media_url: str | None = None
    thumbnail_url: str | None = None
    location: str | None = None
    tags: list[str] = field(default_factory=list)
    favorited: bool = False
    created_at: str | None = None
    updated_at: str | None = None

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
    location: str | None = None
    description: str | None = None
    status: str = "upcoming"  # upcoming, completed, cancelled
    created_by: str = "genie"
    created_at: str | None = None
    updated_at: str | None = None

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

        # start_datetimeからdateとtimeを分離
        date = event_data.get("date", "")
        time = event_data.get("time", "")

        # start_datetimeが提供されている場合は分割
        start_datetime = event_data.get("start_datetime")
        if start_datetime and not date and not time:
            try:
                from datetime import datetime as dt

                # ISO形式をパース (例: "2025-06-30T10:00:00")
                if "T" in start_datetime:
                    dt_obj = dt.fromisoformat(start_datetime.replace("Z", ""))
                    date = dt_obj.strftime("%Y-%m-%d")
                    time = dt_obj.strftime("%H:%M")
            except Exception as e:
                # パースに失敗した場合はそのまま
                pass

        # event_typeからtypeにマッピング
        event_type = event_data.get("event_type") or event_data.get("type", "")

        return cls(
            event_id=event_data.get("id", str(uuid.uuid4())),
            user_id=user_id,
            title=event_data.get("title", ""),
            date=date,
            time=time,
            type=event_type,
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
    highlights: list[str] = field(default_factory=list)
    categories: dict[str, int] = field(default_factory=dict)
    summary: str = ""
    achievements: list[str] = field(default_factory=list)
    created_at: str | None = None
    updated_at: str | None = None

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
    living_area: str = ""  # 居住エリア情報（市区町村レベル）
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
        children = family_data.get("children", [])

        # child_idが無い子供にUUIDを自動付与
        for child in children:
            if "id" not in child or not child["id"]:
                child["id"] = str(uuid.uuid4())

        return cls(
            user_id=user_id,
            parent_name=family_data.get("parent_name", ""),
            family_structure=family_data.get("family_structure", ""),
            concerns=family_data.get("concerns", ""),
            living_area=family_data.get("living_area", ""),
            children=children,
        )

    def to_dict(self) -> dict[str, Any]:
        """辞書形式に変換"""
        return {
            "family_id": self.family_id,
            "user_id": self.user_id,
            "parent_name": self.parent_name,
            "family_structure": self.family_structure,
            "concerns": self.concerns,
            "living_area": self.living_area,
            "children": self.children,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


@dataclass
class NutritionInfo:
    """栄養情報エンティティ"""

    calories: float | None = None
    protein: float | None = None
    carbs: float | None = None
    fat: float | None = None
    fiber: float | None = None

    def to_dict(self) -> dict[str, Any]:
        """辞書形式に変換"""
        return {
            "calories": self.calories,
            "protein": self.protein,
            "carbs": self.carbs,
            "fat": self.fat,
            "fiber": self.fiber,
        }


@dataclass
class PlannedMeal:
    """個別食事プランエンティティ"""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    description: str = ""
    ingredients: list[str] = field(default_factory=list)
    estimated_nutrition: NutritionInfo | None = None
    difficulty: DifficultyLevel = DifficultyLevel.EASY
    prep_time_minutes: int = 10
    tags: list[str] = field(default_factory=list)
    allergens: list[str] = field(default_factory=list)
    recipe_url: str | None = None

    def __post_init__(self):
        """バリデーション"""
        if not self.title.strip():
            raise ValueError("title is required")
        if self.prep_time_minutes < 0:
            raise ValueError("prep_time_minutes must be non-negative")

        if isinstance(self.difficulty, str):
            self.difficulty = DifficultyLevel(self.difficulty)

    def to_dict(self) -> dict[str, Any]:
        """辞書形式に変換"""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "ingredients": self.ingredients,
            "estimated_nutrition": self.estimated_nutrition.to_dict() if self.estimated_nutrition else None,
            "difficulty": self.difficulty.value,
            "prep_time_minutes": self.prep_time_minutes,
            "tags": self.tags,
            "allergens": self.allergens,
            "recipe_url": self.recipe_url,
        }


@dataclass
class DayMealPlan:
    """1日分の食事プランエンティティ"""

    breakfast: PlannedMeal | None = None
    lunch: PlannedMeal | None = None
    dinner: PlannedMeal | None = None
    snack: PlannedMeal | None = None

    def get_meal_by_type(self, meal_type: MealType) -> PlannedMeal | None:
        """食事タイプから食事プランを取得"""
        meal_map = {
            MealType.BREAKFAST: self.breakfast,
            MealType.LUNCH: self.lunch,
            MealType.DINNER: self.dinner,
            MealType.SNACK: self.snack,
        }
        return meal_map.get(meal_type)

    def set_meal_by_type(self, meal_type: MealType, meal: PlannedMeal) -> None:
        """食事タイプで食事プランを設定"""
        if meal_type == MealType.BREAKFAST:
            self.breakfast = meal
        elif meal_type == MealType.LUNCH:
            self.lunch = meal
        elif meal_type == MealType.DINNER:
            self.dinner = meal
        elif meal_type == MealType.SNACK:
            self.snack = meal

    def to_dict(self) -> dict[str, Any]:
        """辞書形式に変換"""
        return {
            "breakfast": self.breakfast.to_dict() if self.breakfast else None,
            "lunch": self.lunch.to_dict() if self.lunch else None,
            "dinner": self.dinner.to_dict() if self.dinner else None,
            "snack": self.snack.to_dict() if self.snack else None,
        }


@dataclass
class NutritionGoals:
    """栄養目標エンティティ"""

    daily_calories: float = 300.0
    daily_protein: float = 15.0
    daily_carbs: float = 45.0
    daily_fat: float = 8.0

    def to_dict(self) -> dict[str, Any]:
        """辞書形式に変換"""
        return {
            "daily_calories": self.daily_calories,
            "daily_protein": self.daily_protein,
            "daily_carbs": self.daily_carbs,
            "daily_fat": self.daily_fat,
        }


@dataclass
class MealPlan:
    """1週間食事プランエンティティ"""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    child_id: str | None = None
    week_start: str = ""  # YYYY-MM-DD format
    title: str = ""
    description: str = ""
    created_by: PlanCreatedBy = PlanCreatedBy.USER
    # 7日分の食事プラン（monday, tuesday, ..., sunday）
    meals: dict[str, DayMealPlan] = field(default_factory=dict)
    nutrition_goals: NutritionGoals | None = None
    notes: str | None = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """バリデーション"""
        if not self.user_id.strip():
            raise ValueError("user_id is required")
        if not self.title.strip():
            raise ValueError("title is required")
        if not self.week_start:
            raise ValueError("week_start is required")

        if isinstance(self.created_by, str):
            self.created_by = PlanCreatedBy(self.created_by)

        # 7日分のキーを初期化
        weekdays = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        for day in weekdays:
            if day not in self.meals:
                self.meals[day] = DayMealPlan()

    @classmethod
    def from_dict(cls, user_id: str, plan_data: dict) -> "MealPlan":
        """辞書データから食事プランエンティティを作成"""
        # 栄養目標の処理
        nutrition_goals = None
        if nutrition_goals_data := plan_data.get("nutrition_goals"):
            nutrition_goals = NutritionGoals(
                daily_calories=nutrition_goals_data.get("daily_calories", 300.0),
                daily_protein=nutrition_goals_data.get("daily_protein", 15.0),
                daily_carbs=nutrition_goals_data.get("daily_carbs", 45.0),
                daily_fat=nutrition_goals_data.get("daily_fat", 8.0),
            )

        # 食事プランの処理
        meals = {}
        meals_data = plan_data.get("meals", {})
        for day_key, day_meals_data in meals_data.items():
            day_plan = DayMealPlan()

            for meal_type_str, meal_data in day_meals_data.items():
                if meal_data:
                    # 栄養情報の処理
                    nutrition_info = None
                    if nutrition_data := meal_data.get("estimated_nutrition"):
                        nutrition_info = NutritionInfo(
                            calories=nutrition_data.get("calories"),
                            protein=nutrition_data.get("protein"),
                            carbs=nutrition_data.get("carbs"),
                            fat=nutrition_data.get("fat"),
                            fiber=nutrition_data.get("fiber"),
                        )

                    planned_meal = PlannedMeal(
                        id=meal_data.get("id", str(uuid.uuid4())),
                        title=meal_data.get("title", ""),
                        description=meal_data.get("description", ""),
                        ingredients=meal_data.get("ingredients", []),
                        estimated_nutrition=nutrition_info,
                        difficulty=DifficultyLevel(meal_data.get("difficulty", DifficultyLevel.EASY.value)),
                        prep_time_minutes=meal_data.get("prep_time_minutes", 10),
                        tags=meal_data.get("tags", []),
                        allergens=meal_data.get("allergens", []),
                        recipe_url=meal_data.get("recipe_url"),
                    )

                    try:
                        meal_type = MealType(meal_type_str)
                        day_plan.set_meal_by_type(meal_type, planned_meal)
                    except ValueError:
                        # 無効な meal_type は無視
                        pass

            meals[day_key] = day_plan

        return cls(
            id=plan_data.get("id", str(uuid.uuid4())),
            user_id=user_id,
            child_id=plan_data.get("child_id"),
            week_start=plan_data.get("week_start", ""),
            title=plan_data.get("title", ""),
            description=plan_data.get("description", ""),
            created_by=PlanCreatedBy(plan_data.get("created_by", PlanCreatedBy.USER.value)),
            meals=meals,
            nutrition_goals=nutrition_goals,
            notes=plan_data.get("notes"),
        )

    def to_dict(self) -> dict[str, Any]:
        """辞書形式に変換"""
        meals_dict = {}
        for day_key, day_plan in self.meals.items():
            meals_dict[day_key] = day_plan.to_dict()

        return {
            "id": self.id,
            "user_id": self.user_id,
            "child_id": self.child_id,
            "week_start": self.week_start,
            "title": self.title,
            "description": self.description,
            "created_by": self.created_by.value,
            "meals": meals_dict,
            "nutrition_goals": self.nutrition_goals.to_dict() if self.nutrition_goals else None,
            "notes": self.notes,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


@dataclass
class User:
    """ユーザーエンティティ（Google OAuth統合）"""

    google_id: str = ""  # Google OAuth User ID (プライマリキー)
    email: str = ""
    name: str = ""
    picture_url: str | None = None
    locale: str | None = None  # 言語設定 (ja, en, etc.)
    verified_email: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    last_login: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """バリデーション"""
        if not self.google_id.strip():
            raise ValueError("google_id is required")
        if not self.email.strip():
            raise ValueError("email is required")
        if not self.name.strip():
            raise ValueError("name is required")

    @classmethod
    def from_google_oauth(cls, oauth_user_info: dict) -> "User":
        """Google OAuth情報からユーザーエンティティを作成"""
        return cls(
            google_id=oauth_user_info.get("sub", ""),  # Google User ID
            email=oauth_user_info.get("email", ""),
            name=oauth_user_info.get("name", ""),
            picture_url=oauth_user_info.get("picture"),
            locale=oauth_user_info.get("locale"),
            verified_email=oauth_user_info.get("email_verified", False),
        )

    def update_last_login(self) -> None:
        """最終ログイン時刻を更新"""
        self.last_login = datetime.now()
        self.updated_at = datetime.now()

    def to_dict(self) -> dict[str, Any]:
        """辞書形式に変換"""
        return {
            "google_id": self.google_id,
            "email": self.email,
            "name": self.name,
            "picture_url": self.picture_url,
            "locale": self.locale,
            "verified_email": self.verified_email,
            "created_at": self.created_at.isoformat(),
            "last_login": self.last_login.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


@dataclass
class SearchHistoryEntry:
    """検索履歴エンティティ"""

    id: str
    user_id: str
    query: str
    search_type: str  # web, internal, agent, tool
    results_count: int
    timestamp: datetime
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """バリデーション"""
        if not self.id.strip():
            raise ValueError("id is required")
        if not self.user_id.strip():
            raise ValueError("user_id is required")
        if not self.query.strip():
            raise ValueError("query is required")
        if self.results_count < 0:
            raise ValueError("results_count must be non-negative")

    def to_dict(self) -> dict[str, Any]:
        """辞書形式に変換"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "query": self.query,
            "search_type": self.search_type,
            "results_count": self.results_count,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
        }
