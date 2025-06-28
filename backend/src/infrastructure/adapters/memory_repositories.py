"""In-memory repository implementations for GenieUs v2.0
初期実装用メモリ内リポジトリ（後でPostgreSQL実装に変更予定）
"""

from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any

from src.domain.entities import (
    Child,
    ChildRecord,
    EffortReport,
    EventType,
    ImageRecordingData,
    PredictionResult,
    PredictionType,
    SearchHistoryEntry,
    VoiceRecordingData,
)
from src.domain.repositories import (
    ChildRecordRepository,
    ChildRepository,
    EffortReportRepository,
    FamilyContextRepository,
    ImageRecordingRepository,
    PredictionRepository,
    SearchHistoryRepository,
    VoiceRecordingRepository,
)


class MemoryChildRecordRepository(ChildRecordRepository):
    """子供記録メモリリポジトリ"""

    def __init__(self):
        self._records: dict[str, ChildRecord] = {}
        self._child_index: dict[str, list[str]] = defaultdict(list)

    async def save(self, record: ChildRecord) -> ChildRecord:
        """記録保存"""
        record.updated_at = datetime.now()
        self._records[record.id] = record

        # インデックス更新
        if record.id not in self._child_index[record.child_id]:
            self._child_index[record.child_id].append(record.id)

        return record

    async def find_by_id(self, record_id: str) -> ChildRecord | None:
        """ID検索"""
        return self._records.get(record_id)

    async def find_by_child_id(
        self,
        child_id: str,
        event_type: EventType | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        limit: int = 100,
    ) -> list[ChildRecord]:
        """子供ID・条件での検索"""
        record_ids = self._child_index.get(child_id, [])
        records = []

        for record_id in record_ids:
            record = self._records.get(record_id)
            if not record:
                continue

            # 条件フィルタリング
            if event_type and record.event_type != event_type:
                continue
            if start_date and record.timestamp < start_date:
                continue
            if end_date and record.timestamp > end_date:
                continue

            records.append(record)

        # 時間順ソート（新しい順）
        records.sort(key=lambda x: x.timestamp, reverse=True)
        return records[:limit]

    async def find_recent_by_child_id(
        self,
        child_id: str,
        days: int = 7,
        event_type: EventType | None = None,
    ) -> list[ChildRecord]:
        """直近N日間の記録取得"""
        start_date = datetime.now() - timedelta(days=days)
        return await self.find_by_child_id(child_id=child_id, event_type=event_type, start_date=start_date)

    async def find_patterns(self, child_id: str, pattern_window_days: int = 30) -> list[dict[str, Any]]:
        """パターン分析用データ取得"""
        records = await self.find_recent_by_child_id(child_id, pattern_window_days)

        # 簡単なパターン分析（実装例）
        patterns = []
        event_counts = defaultdict(int)

        for record in records:
            event_counts[record.event_type.value] += 1

        for event_type, count in event_counts.items():
            if count > 3:  # 3回以上出現したイベント
                patterns.append(
                    {
                        "pattern": f"{event_type}の頻繁な記録",
                        "confidence": min(count / 10.0, 1.0),
                        "occurrences": count,
                    },
                )

        return patterns

    async def delete(self, record_id: str) -> bool:
        """記録削除"""
        record = self._records.get(record_id)
        if not record:
            return False

        # インデックスからも削除
        if record_id in self._child_index[record.child_id]:
            self._child_index[record.child_id].remove(record_id)

        del self._records[record_id]
        return True


class MemoryChildRepository(ChildRepository):
    """子供メモリリポジトリ"""

    def __init__(self):
        self._children: dict[str, Child] = {}
        self._parent_index: dict[str, list[str]] = defaultdict(list)

    async def save(self, child: Child) -> Child:
        """子供情報保存"""
        child.updated_at = datetime.now()
        self._children[child.id] = child

        # 親インデックス更新
        for parent_id in child.parent_ids:
            if child.id not in self._parent_index[parent_id]:
                self._parent_index[parent_id].append(child.id)

        return child

    async def find_by_id(self, child_id: str) -> Child | None:
        """ID検索"""
        return self._children.get(child_id)

    async def find_by_parent_id(self, parent_id: str) -> list[Child]:
        """親IDで検索"""
        child_ids = self._parent_index.get(parent_id, [])
        return [self._children[child_id] for child_id in child_ids if child_id in self._children]

    async def delete(self, child_id: str) -> bool:
        """子供情報削除"""
        child = self._children.get(child_id)
        if not child:
            return False

        # 親インデックスからも削除
        for parent_id in child.parent_ids:
            if child_id in self._parent_index[parent_id]:
                self._parent_index[parent_id].remove(child_id)

        del self._children[child_id]
        return True


class MemoryPredictionRepository(PredictionRepository):
    """予測結果メモリリポジトリ"""

    def __init__(self):
        self._predictions: dict[str, PredictionResult] = {}
        self._child_index: dict[str, list[str]] = defaultdict(list)

    async def save(self, prediction: PredictionResult) -> PredictionResult:
        """予測結果保存"""
        self._predictions[prediction.id] = prediction

        # インデックス更新
        if prediction.id not in self._child_index[prediction.child_id]:
            self._child_index[prediction.child_id].append(prediction.id)

        return prediction

    async def find_by_id(self, prediction_id: str) -> PredictionResult | None:
        """ID検索"""
        return self._predictions.get(prediction_id)

    async def find_by_child_id(
        self,
        child_id: str,
        prediction_type: PredictionType | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> list[PredictionResult]:
        """子供ID・条件での検索"""
        prediction_ids = self._child_index.get(child_id, [])
        predictions = []

        for prediction_id in prediction_ids:
            prediction = self._predictions.get(prediction_id)
            if not prediction:
                continue

            # 条件フィルタリング
            if prediction_type and prediction.prediction_type != prediction_type:
                continue
            if start_date and prediction.prediction_date < start_date:
                continue
            if end_date and prediction.prediction_date > end_date:
                continue

            predictions.append(prediction)

        # 日付順ソート（新しい順）
        predictions.sort(key=lambda x: x.prediction_date, reverse=True)
        return predictions

    async def find_latest_prediction(
        self,
        child_id: str,
        prediction_type: PredictionType,
    ) -> PredictionResult | None:
        """最新の予測取得"""
        predictions = await self.find_by_child_id(child_id, prediction_type)
        return predictions[0] if predictions else None

    async def find_todays_predictions(self, child_id: str) -> list[PredictionResult]:
        """今日の予測一覧取得"""
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow = today + timedelta(days=1)

        return await self.find_by_child_id(child_id=child_id, start_date=today, end_date=tomorrow)

    async def delete_old_predictions(self, days_old: int = 30) -> int:
        """古い予測データの削除"""
        cutoff_date = datetime.now() - timedelta(days=days_old)
        deleted_count = 0

        to_delete = []
        for prediction_id, prediction in self._predictions.items():
            if prediction.prediction_date < cutoff_date:
                to_delete.append(prediction_id)

        for prediction_id in to_delete:
            prediction = self._predictions[prediction_id]
            # インデックスからも削除
            if prediction_id in self._child_index[prediction.child_id]:
                self._child_index[prediction.child_id].remove(prediction_id)
            del self._predictions[prediction_id]
            deleted_count += 1

        return deleted_count


class MemoryEffortReportRepository(EffortReportRepository):
    """努力レポートメモリリポジトリ"""

    def __init__(self):
        self._reports: dict[str, EffortReport] = {}
        self._parent_child_index: dict[str, list[str]] = defaultdict(list)

    async def save(self, report: EffortReport) -> EffortReport:
        """レポート保存"""
        self._reports[report.id] = report

        # インデックス更新
        key = f"{report.parent_id}:{report.child_id}"
        if report.id not in self._parent_child_index[key]:
            self._parent_child_index[key].append(report.id)

        return report

    async def find_by_id(self, report_id: str) -> EffortReport | None:
        """ID検索"""
        return self._reports.get(report_id)

    async def find_by_parent_and_child(
        self,
        parent_id: str,
        child_id: str,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> list[EffortReport]:
        """親・子供IDで検索"""
        key = f"{parent_id}:{child_id}"
        report_ids = self._parent_child_index.get(key, [])
        reports = []

        for report_id in report_ids:
            report = self._reports.get(report_id)
            if not report:
                continue

            # 条件フィルタリング
            if start_date and report.period_end < start_date:
                continue
            if end_date and report.period_start > end_date:
                continue

            reports.append(report)

        # 日付順ソート（新しい順）
        reports.sort(key=lambda x: x.created_at, reverse=True)
        return reports

    async def find_latest_report(self, parent_id: str, child_id: str) -> EffortReport | None:
        """最新レポート取得"""
        reports = await self.find_by_parent_and_child(parent_id, child_id)
        return reports[0] if reports else None

    async def delete(self, report_id: str) -> bool:
        """レポート削除"""
        report = self._reports.get(report_id)
        if not report:
            return False

        # インデックスからも削除
        key = f"{report.parent_id}:{report.child_id}"
        if report_id in self._parent_child_index[key]:
            self._parent_child_index[key].remove(report_id)

        del self._reports[report_id]
        return True


class MemoryVoiceRecordingRepository(VoiceRecordingRepository):
    """音声記録メモリリポジトリ"""

    def __init__(self):
        self._recordings: dict[str, VoiceRecordingData] = {}

    async def save(self, voice_data: VoiceRecordingData) -> VoiceRecordingData:
        """音声記録保存"""
        self._recordings[voice_data.id] = voice_data
        return voice_data

    async def find_by_id(self, recording_id: str) -> VoiceRecordingData | None:
        """ID検索"""
        return self._recordings.get(recording_id)

    async def find_pending_processing(self) -> list[VoiceRecordingData]:
        """処理待ち音声記録取得"""
        return [recording for recording in self._recordings.values() if recording.processing_status == "pending"]

    async def update_processing_status(
        self,
        recording_id: str,
        status: str,
        error_message: str | None = None,
    ) -> bool:
        """処理状況更新"""
        recording = self._recordings.get(recording_id)
        if not recording:
            return False

        recording.processing_status = status
        recording.error_message = error_message
        return True


class MemoryImageRecordingRepository(ImageRecordingRepository):
    """画像記録メモリリポジトリ"""

    def __init__(self):
        self._recordings: dict[str, ImageRecordingData] = {}

    async def save(self, image_data: ImageRecordingData) -> ImageRecordingData:
        """画像記録保存"""
        self._recordings[image_data.id] = image_data
        return image_data

    async def find_by_id(self, recording_id: str) -> ImageRecordingData | None:
        """ID検索"""
        return self._recordings.get(recording_id)

    async def find_pending_processing(self) -> list[ImageRecordingData]:
        """処理待ち画像記録取得"""
        return [recording for recording in self._recordings.values() if recording.processing_status == "pending"]

    async def update_processing_status(
        self,
        recording_id: str,
        status: str,
        error_message: str | None = None,
    ) -> bool:
        """処理状況更新"""
        recording = self._recordings.get(recording_id)
        if not recording:
            return False

        recording.processing_status = status
        recording.error_message = error_message
        return True


class MemoryFamilyContextRepository(FamilyContextRepository):
    """家族コンテキスト分析用メモリリポジトリ"""

    def __init__(self, child_record_repo: MemoryChildRecordRepository):
        self.child_record_repo = child_record_repo

    async def find_related_events(self, child_id: str, query_context: str, days_back: int = 30) -> list[dict[str, Any]]:
        """クエリコンテキストに関連するイベント検索"""
        records = await self.child_record_repo.find_recent_by_child_id(child_id, days_back)

        # 簡単なキーワードマッチング（実際はNLPエンジンを使用）
        keywords = query_context.lower().split()
        sleep_keywords = ["睡眠", "寝る", "夜泣き", "昼寝"]
        feeding_keywords = ["食事", "ミルク", "離乳食", "授乳"]

        related_events = []
        for record in records:
            # イベントタイプとキーワードのマッチング
            is_related = False
            if (any(kw in keywords for kw in sleep_keywords) and record.event_type == EventType.SLEEP) or (
                any(kw in keywords for kw in feeding_keywords) and record.event_type == EventType.FEEDING
            ):
                is_related = True

            if is_related:
                days_ago = (datetime.now() - record.timestamp).days
                related_events.append(
                    {
                        "date": f"{days_ago}日前",
                        "event": f"{record.event_type.value}",
                        "impact": "状況変化の要因の可能性",
                        "confidence": 0.7,
                    },
                )

        return related_events[:5]  # 最大5件

    async def find_causal_patterns(
        self,
        child_id: str,
        event_types: list[EventType],
        correlation_window_hours: int = 24,
    ) -> list[dict[str, Any]]:
        """因果関係パターン分析"""
        records = await self.child_record_repo.find_recent_by_child_id(child_id, 14)

        # 簡単な相関分析（実際はより高度な統計手法を使用）
        patterns = []
        if len(records) > 10:
            patterns.append(
                {"pattern": "食事後の睡眠パターン", "confidence": 0.75, "description": "食事の30分後に睡眠する傾向"},
            )

        return patterns

    async def find_seasonal_patterns(
        self,
        child_id: str,
        event_type: EventType,
        weeks_back: int = 12,
    ) -> list[dict[str, Any]]:
        """季節・曜日パターン分析"""
        records = await self.child_record_repo.find_recent_by_child_id(child_id, weeks_back * 7, event_type)

        # 曜日パターンの簡単な分析
        weekday_counts = defaultdict(int)
        for record in records:
            weekday = record.timestamp.weekday()
            weekday_counts[weekday] += 1

        patterns = []
        if weekday_counts:
            max_day = max(weekday_counts, key=weekday_counts.get)
            weekdays = ["月", "火", "水", "木", "金", "土", "日"]
            patterns.append(
                {
                    "pattern": f"{weekdays[max_day]}曜日のパターン",
                    "confidence": 0.6,
                    "description": f"{weekdays[max_day]}曜日に{event_type.value}が多い傾向",
                },
            )

        return patterns

    async def find_milestone_correlations(self, child_id: str, milestone_events: list[str]) -> list[dict[str, Any]]:
        """マイルストーンとの相関分析"""
        records = await self.child_record_repo.find_recent_by_child_id(child_id, 30)

        # マイルストーン記録の検索
        milestone_records = [record for record in records if record.event_type == EventType.MILESTONE]

        correlations = []
        if milestone_records:
            correlations.append(
                {
                    "milestone": "発達段階の変化",
                    "correlation": "行動パターンの変化",
                    "confidence": 0.8,
                    "impact": "新しい成長段階に適応中",
                },
            )

        return correlations


class MemorySearchHistoryRepository(SearchHistoryRepository):
    """検索履歴メモリリポジトリ"""

    def __init__(self):
        self._entries: dict[str, SearchHistoryEntry] = {}
        self._user_index: dict[str, list[str]] = defaultdict(list)

    async def save(self, entry: SearchHistoryEntry) -> SearchHistoryEntry:
        """検索履歴保存"""
        self._entries[entry.id] = entry

        # インデックス更新
        if entry.id not in self._user_index[entry.user_id]:
            self._user_index[entry.user_id].append(entry.id)

        return entry

    async def find_by_user_id(
        self,
        user_id: str,
        search_type: str | None = None,
        start_date: datetime | None = None,
        limit: int = 100,
    ) -> list[SearchHistoryEntry]:
        """ユーザーIDで検索履歴取得"""
        entry_ids = self._user_index.get(user_id, [])
        entries = []

        for entry_id in entry_ids:
            entry = self._entries.get(entry_id)
            if not entry:
                continue

            # 条件フィルタリング
            if search_type and entry.search_type != search_type:
                continue
            if start_date and entry.timestamp < start_date:
                continue

            entries.append(entry)

        # 日付順ソート（新しい順）
        entries.sort(key=lambda x: x.timestamp, reverse=True)
        return entries[:limit]

    async def get_popular_queries(
        self,
        start_date: datetime | None = None,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        """人気クエリ取得"""
        query_counts: dict[str, int] = defaultdict(int)

        for entry in self._entries.values():
            # 期間フィルタリング
            if start_date and entry.timestamp < start_date:
                continue

            query_counts[entry.query] += 1

        # カウント順ソート
        sorted_queries = sorted(query_counts.items(), key=lambda x: x[1], reverse=True)

        return [{"query": query, "count": count} for query, count in sorted_queries[:limit]]

    async def delete_by_id(self, history_id: str, user_id: str) -> int:
        """特定履歴削除"""
        entry = self._entries.get(history_id)
        if not entry or entry.user_id != user_id:
            return 0

        # インデックスからも削除
        if history_id in self._user_index[user_id]:
            self._user_index[user_id].remove(history_id)

        del self._entries[history_id]
        return 1

    async def delete_by_user_id(self, user_id: str) -> int:
        """ユーザーの全履歴削除"""
        entry_ids = self._user_index.get(user_id, [])
        deleted_count = 0

        for entry_id in entry_ids[:]:  # コピーを作って安全に削除
            if entry_id in self._entries:
                del self._entries[entry_id]
                deleted_count += 1

        # インデックスをクリア
        self._user_index[user_id] = []
        return deleted_count


# リポジトリファクトリ（DI用）
class MemoryRepositoryFactory:
    """メモリリポジトリファクトリ"""

    def __init__(self):
        # 共有インスタンス（データ整合性のため）
        self._child_record_repo = MemoryChildRecordRepository()
        self._child_repo = MemoryChildRepository()
        self._prediction_repo = MemoryPredictionRepository()
        self._effort_report_repo = MemoryEffortReportRepository()
        self._voice_recording_repo = MemoryVoiceRecordingRepository()
        self._image_recording_repo = MemoryImageRecordingRepository()
        self._family_context_repo = MemoryFamilyContextRepository(self._child_record_repo)
        self._search_history_repo = MemorySearchHistoryRepository()

    def get_child_record_repository(self) -> ChildRecordRepository:
        return self._child_record_repo

    def get_child_repository(self) -> ChildRepository:
        return self._child_repo

    def get_prediction_repository(self) -> PredictionRepository:
        return self._prediction_repo

    def get_effort_report_repository(self) -> EffortReportRepository:
        return self._effort_report_repo

    def get_voice_recording_repository(self) -> VoiceRecordingRepository:
        return self._voice_recording_repo

    def get_image_recording_repository(self) -> ImageRecordingRepository:
        return self._image_recording_repo

    def get_family_context_repository(self) -> FamilyContextRepository:
        return self._family_context_repo

    def get_search_history_repository(self) -> SearchHistoryRepository:
        return self._search_history_repo
