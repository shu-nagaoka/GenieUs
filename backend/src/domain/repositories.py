"""Repository interfaces for GenieUs v2.0
ドメイン層のリポジトリインターフェース定義
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

from src.domain.entities import (
    Child,
    ChildRecord,
    EffortReport,
    EventType,
    ImageRecordingData,
    PredictionResult,
    PredictionType,
    VoiceRecordingData,
)


class ChildRecordRepository(ABC):
    """子供記録リポジトリインターフェース"""

    @abstractmethod
    async def save(self, record: ChildRecord) -> ChildRecord:
        """記録保存"""
        pass

    @abstractmethod
    async def find_by_id(self, record_id: str) -> ChildRecord | None:
        """ID検索"""
        pass

    @abstractmethod
    async def find_by_child_id(
        self,
        child_id: str,
        event_type: EventType | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        limit: int = 100,
    ) -> list[ChildRecord]:
        """子供ID・条件での検索"""
        pass

    @abstractmethod
    async def find_recent_by_child_id(
        self,
        child_id: str,
        days: int = 7,
        event_type: EventType | None = None,
    ) -> list[ChildRecord]:
        """直近N日間の記録取得"""
        pass

    @abstractmethod
    async def find_patterns(self, child_id: str, pattern_window_days: int = 30) -> list[dict[str, Any]]:
        """パターン分析用データ取得"""
        pass

    @abstractmethod
    async def delete(self, record_id: str) -> bool:
        """記録削除"""
        pass


class ChildRepository(ABC):
    """子供リポジトリインターフェース"""

    @abstractmethod
    async def save(self, child: Child) -> Child:
        """子供情報保存"""
        pass

    @abstractmethod
    async def find_by_id(self, child_id: str) -> Child | None:
        """ID検索"""
        pass

    @abstractmethod
    async def find_by_parent_id(self, parent_id: str) -> list[Child]:
        """親IDで検索"""
        pass

    @abstractmethod
    async def delete(self, child_id: str) -> bool:
        """子供情報削除"""
        pass


class PredictionRepository(ABC):
    """予測結果リポジトリインターフェース"""

    @abstractmethod
    async def save(self, prediction: PredictionResult) -> PredictionResult:
        """予測結果保存"""
        pass

    @abstractmethod
    async def find_by_id(self, prediction_id: str) -> PredictionResult | None:
        """ID検索"""
        pass

    @abstractmethod
    async def find_by_child_id(
        self,
        child_id: str,
        prediction_type: PredictionType | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> list[PredictionResult]:
        """子供ID・条件での検索"""
        pass

    @abstractmethod
    async def find_latest_prediction(
        self,
        child_id: str,
        prediction_type: PredictionType,
    ) -> PredictionResult | None:
        """最新の予測取得"""
        pass

    @abstractmethod
    async def find_todays_predictions(self, child_id: str) -> list[PredictionResult]:
        """今日の予測一覧取得"""
        pass

    @abstractmethod
    async def delete_old_predictions(self, days_old: int = 30) -> int:
        """古い予測データの削除"""
        pass


class EffortReportRepository(ABC):
    """努力レポートリポジトリインターフェース"""

    @abstractmethod
    async def save(self, report: EffortReport) -> EffortReport:
        """レポート保存"""
        pass

    @abstractmethod
    async def find_by_id(self, report_id: str) -> EffortReport | None:
        """ID検索"""
        pass

    @abstractmethod
    async def find_by_parent_and_child(
        self,
        parent_id: str,
        child_id: str,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> list[EffortReport]:
        """親・子供IDで検索"""
        pass

    @abstractmethod
    async def find_latest_report(self, parent_id: str, child_id: str) -> EffortReport | None:
        """最新レポート取得"""
        pass

    @abstractmethod
    async def delete(self, report_id: str) -> bool:
        """レポート削除"""
        pass


class VoiceRecordingRepository(ABC):
    """音声記録リポジトリインターフェース"""

    @abstractmethod
    async def save(self, voice_data: VoiceRecordingData) -> VoiceRecordingData:
        """音声記録保存"""
        pass

    @abstractmethod
    async def find_by_id(self, recording_id: str) -> VoiceRecordingData | None:
        """ID検索"""
        pass

    @abstractmethod
    async def find_pending_processing(self) -> list[VoiceRecordingData]:
        """処理待ち音声記録取得"""
        pass

    @abstractmethod
    async def update_processing_status(
        self,
        recording_id: str,
        status: str,
        error_message: str | None = None,
    ) -> bool:
        """処理状況更新"""
        pass


class ImageRecordingRepository(ABC):
    """画像記録リポジトリインターフェース"""

    @abstractmethod
    async def save(self, image_data: ImageRecordingData) -> ImageRecordingData:
        """画像記録保存"""
        pass

    @abstractmethod
    async def find_by_id(self, recording_id: str) -> ImageRecordingData | None:
        """ID検索"""
        pass

    @abstractmethod
    async def find_pending_processing(self) -> list[ImageRecordingData]:
        """処理待ち画像記録取得"""
        pass

    @abstractmethod
    async def update_processing_status(
        self,
        recording_id: str,
        status: str,
        error_message: str | None = None,
    ) -> bool:
        """処理状況更新"""
        pass


class FamilyContextRepository(ABC):
    """家族コンテキスト分析用リポジトリインターフェース"""

    @abstractmethod
    async def find_related_events(self, child_id: str, query_context: str, days_back: int = 30) -> list[dict[str, Any]]:
        """クエリコンテキストに関連するイベント検索"""
        pass

    @abstractmethod
    async def find_causal_patterns(
        self,
        child_id: str,
        event_types: list[EventType],
        correlation_window_hours: int = 24,
    ) -> list[dict[str, Any]]:
        """因果関係パターン分析"""
        pass

    @abstractmethod
    async def find_seasonal_patterns(
        self,
        child_id: str,
        event_type: EventType,
        weeks_back: int = 12,
    ) -> list[dict[str, Any]]:
        """季節・曜日パターン分析"""
        pass

    @abstractmethod
    async def find_milestone_correlations(self, child_id: str, milestone_events: list[str]) -> list[dict[str, Any]]:
        """マイルストーンとの相関分析"""
        pass


class PredictionAnalyticsRepository(ABC):
    """予測分析用リポジトリインターフェース"""

    @abstractmethod
    async def calculate_prediction_accuracy(
        self,
        child_id: str,
        prediction_type: PredictionType,
        days_back: int = 30,
    ) -> dict[str, float]:
        """予測精度計算"""
        pass

    @abstractmethod
    async def find_successful_predictions(
        self,
        child_id: str,
        confidence_threshold: float = 0.7,
    ) -> list[PredictionResult]:
        """成功した予測の検索"""
        pass

    @abstractmethod
    async def generate_trend_data(
        self,
        child_id: str,
        event_type: EventType,
        days_back: int = 30,
    ) -> list[dict[str, Any]]:
        """トレンドデータ生成"""
        pass


class EffortAnalyticsRepository(ABC):
    """努力分析用リポジトリインターフェース"""

    @abstractmethod
    async def calculate_parental_metrics(
        self,
        parent_id: str,
        child_id: str,
        start_date: datetime,
        end_date: datetime,
    ) -> dict[str, Any]:
        """親の行動指標計算"""
        pass

    @abstractmethod
    async def find_effort_correlations(
        self,
        parent_id: str,
        child_id: str,
        weeks_back: int = 4,
    ) -> list[dict[str, Any]]:
        """努力と成長の相関分析"""
        pass

    @abstractmethod
    async def compare_periods(
        self,
        parent_id: str,
        child_id: str,
        current_period_days: int = 7,
        comparison_period_days: int = 7,
    ) -> dict[str, Any]:
        """期間比較分析"""
        pass
