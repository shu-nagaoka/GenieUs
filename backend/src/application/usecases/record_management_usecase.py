"""記録管理UseCase"""

import logging
from datetime import datetime, timedelta
from typing import Any

from src.domain.entities import ChildRecord, EventType
from src.domain.repositories import ChildRecordRepository


class RecordManagementUseCase:
    """子どもの記録管理のビジネスロジック"""

    def __init__(self, child_record_repository: ChildRecordRepository, logger: logging.Logger) -> None:
        self.child_record_repository = child_record_repository
        self.logger = logger

    async def save_child_record(
        self,
        child_id: str,
        event_type: str,
        description: str,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """子どもの記録を保存

        Args:
            child_id: 子どものID
            event_type: イベントタイプ（feeding, sleep, mood等）
            description: 記録の説明
            metadata: 追加のメタデータ

        Returns:
            Dict[str, Any]: 保存結果

        """
        try:
            self.logger.info(f"記録保存開始: child_id={child_id}, event_type={event_type}")

            # イベントタイプの検証・変換
            try:
                validated_event_type = EventType(event_type.lower())
            except ValueError:
                self.logger.warning(f"無効なイベントタイプ: {event_type}, デフォルトでOTHERを使用")
                validated_event_type = EventType.OTHER

            # 記録エンティティの作成
            record = ChildRecord(
                id=f"{child_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                child_id=child_id,
                event_type=validated_event_type,
                description=description,
                timestamp=datetime.now(),
                metadata=metadata or {},
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )

            # リポジトリに保存
            saved_record = await self.child_record_repository.save(record)

            result = {
                "success": True,
                "record_id": saved_record.id,
                "child_id": child_id,
                "event_type": saved_record.event_type.value,
                "timestamp": saved_record.timestamp.isoformat(),
            }

            self.logger.info(f"記録保存完了: record_id={saved_record.id}")
            return result

        except Exception as e:
            self.logger.error(f"記録保存UseCase実行エラー: {e}")
            return self._create_error_response(str(e))

    async def get_child_records(
        self,
        child_id: str,
        event_type: str | None = None,
        days_back: int = 7,
        limit: int = 50,
    ) -> dict[str, Any]:
        """子どもの記録を取得

        Args:
            child_id: 子どものID
            event_type: フィルターするイベントタイプ（オプション）
            days_back: 取得する過去の日数
            limit: 最大取得数

        Returns:
            Dict[str, Any]: 記録一覧

        """
        try:
            self.logger.info(f"記録取得開始: child_id={child_id}, event_type={event_type}, days_back={days_back}")

            # イベントタイプの検証
            filter_event_type = None
            if event_type:
                try:
                    filter_event_type = EventType(event_type.lower())
                except ValueError:
                    self.logger.warning(f"無効なイベントタイプでフィルター: {event_type}")

            # 期間の計算
            start_date = datetime.now() - timedelta(days=days_back)

            # リポジトリから記録を取得
            records = await self.child_record_repository.find_by_child_id(
                child_id=child_id,
                event_type=filter_event_type,
                start_date=start_date,
                limit=limit,
            )

            # レスポンス形式への変換
            records_data = []
            for record in records:
                record_data = {
                    "id": record.id,
                    "event_type": record.event_type.value,
                    "description": record.description,
                    "timestamp": record.timestamp.isoformat(),
                    "metadata": record.metadata,
                    "days_ago": (datetime.now() - record.timestamp).days,
                }
                records_data.append(record_data)

            result = {
                "success": True,
                "child_id": child_id,
                "records": records_data,
                "total_count": len(records_data),
                "filter_event_type": event_type,
                "days_back": days_back,
            }

            self.logger.info(f"記録取得完了: {len(records_data)}件")
            return result

        except Exception as e:
            self.logger.error(f"記録取得UseCase実行エラー: {e}")
            return self._create_error_response(str(e))

    async def get_record_patterns(self, child_id: str, analysis_days: int = 30) -> dict[str, Any]:
        """記録パターンの分析

        Args:
            child_id: 子どものID
            analysis_days: 分析対象の日数

        Returns:
            Dict[str, Any]: パターン分析結果

        """
        try:
            self.logger.info(f"パターン分析開始: child_id={child_id}, analysis_days={analysis_days}")

            # パターン分析の実行
            patterns = await self.child_record_repository.find_patterns(child_id, analysis_days)

            # ビジネスロジック: パターンの後処理・解釈
            interpreted_patterns = self._interpret_patterns(patterns)

            result = {
                "success": True,
                "child_id": child_id,
                "analysis_period_days": analysis_days,
                "patterns": interpreted_patterns,
                "pattern_count": len(interpreted_patterns),
            }

            self.logger.info(f"パターン分析完了: {len(interpreted_patterns)}件のパターン検出")
            return result

        except Exception as e:
            self.logger.error(f"パターン分析UseCase実行エラー: {e}")
            return self._create_error_response(str(e))

    def _interpret_patterns(self, patterns: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """パターンデータの解釈・拡張"""
        interpreted = []

        for pattern in patterns:
            confidence = pattern.get("confidence", 0)
            pattern_type = pattern.get("pattern", "")

            # 信頼度による解釈の追加
            interpretation = ""
            if confidence > 0.7:
                interpretation = "安定したパターンです。継続して記録することをお勧めします。"
            elif confidence > 0.4:
                interpretation = "ある程度のパターンが見られます。もう少し観察してみましょう。"
            else:
                interpretation = "まだパターンは明確ではありません。継続的な記録が必要です。"

            interpreted_pattern = {
                **pattern,
                "interpretation": interpretation,
                "confidence_level": "高" if confidence > 0.7 else "中" if confidence > 0.4 else "低",
            }
            interpreted.append(interpreted_pattern)

        return interpreted

    def _create_error_response(self, error_message: str) -> dict[str, Any]:
        """エラー時のレスポンス作成"""
        return {
            "success": False,
            "error": error_message,
            "records": [],
            "total_count": 0,
        }
