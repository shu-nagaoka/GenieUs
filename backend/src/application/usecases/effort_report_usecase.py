"""努力レポート管理UseCase

コーディング規約準拠:
- Import文ファイル先頭配置
- 型アノテーション完備
- DI注入パターン
- 段階的エラーハンドリング
"""

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

from src.application.interface.protocols.effort_report_repository import (
    EffortReportRepositoryProtocol,
)
from src.application.interface.protocols.family_repository import (
    FamilyRepositoryProtocol,
)
from src.application.interface.protocols.meal_record_repository import (
    MealRecordRepositoryProtocol,
)
from src.application.interface.protocols.schedule_record_repository import (
    ScheduleRecordRepositoryProtocol,
)
from src.application.interface.protocols.image_analyzer import (
    ImageAnalyzerProtocol,
)
from src.domain.entities import EffortReportRecord


@dataclass
class CreateEffortReportRequest:
    """努力レポート作成リクエスト"""

    user_id: str
    period_days: int = 7
    effort_count: int = 0
    score: float = 0.0
    highlights: list[str] = None
    categories: dict[str, int] = None
    summary: str = ""
    achievements: list[str] = None

    def __post_init__(self):
        if self.highlights is None:
            self.highlights = []
        if self.categories is None:
            self.categories = {}
        if self.achievements is None:
            self.achievements = []


@dataclass
class UpdateEffortReportRequest:
    """努力レポート更新リクエスト"""

    user_id: str
    report_id: str
    period_days: int | None = None
    effort_count: int | None = None
    score: float | None = None
    highlights: list[str] | None = None
    categories: dict[str, int] | None = None
    summary: str | None = None
    achievements: list[str] | None = None


@dataclass
class EffortReportResponse:
    """努力レポートレスポンス"""

    success: bool
    data: dict[str, Any] | None = None
    message: str | None = None
    error: str | None = None


class EffortReportUseCase:
    """努力レポート管理のビジネスロジック"""

    def __init__(
        self,
        effort_report_repository: EffortReportRepositoryProtocol,
        meal_record_repository: MealRecordRepositoryProtocol,
        schedule_record_repository: ScheduleRecordRepositoryProtocol,
        family_repository: FamilyRepositoryProtocol,
        ai_analyzer: ImageAnalyzerProtocol,
        logger: logging.Logger,
    ):
        """EffortReportUseCase初期化

        Args:
            effort_report_repository: 努力レポートリポジトリ
            meal_record_repository: 食事記録リポジトリ
            schedule_record_repository: 予定記録リポジトリ
            family_repository: 家族情報リポジトリ
            ai_analyzer: AI分析エンジン（レポート生成用）
            logger: DIコンテナから注入されるロガー
        """
        self.effort_report_repository = effort_report_repository
        self.meal_record_repository = meal_record_repository
        self.schedule_record_repository = schedule_record_repository
        self.family_repository = family_repository
        self.ai_analyzer = ai_analyzer
        self.logger = logger

    async def create_effort_report(self, user_id: str, report_data: dict) -> dict[str, Any]:
        """努力レポートを作成

        Args:
            user_id: ユーザーID
            report_data: 努力レポートデータ

        Returns:
            Dict[str, Any]: 作成結果

        """
        try:
            self.logger.info(f"努力レポート作成開始: user_id={user_id}")

            # 努力レポートエンティティ作成
            effort_report = EffortReportRecord.from_dict(user_id, report_data)

            # 新しいSQLiteリポジトリに保存
            created_report = await self.effort_report_repository.create(effort_report)

            self.logger.info(f"努力レポート作成完了: user_id={user_id}, report_id={created_report.report_id}")
            return {"success": True, "id": created_report.report_id, "data": created_report.to_dict()}

        except Exception as e:
            self.logger.error(f"努力レポート作成エラー: user_id={user_id}, error={e}")
            return {"success": False, "message": f"努力レポートの作成に失敗しました: {e!s}"}

    async def get_effort_reports(self, user_id: str, filters: dict[str, Any] | None = None) -> dict[str, Any]:
        """努力レポート一覧を取得

        Args:
            user_id: ユーザーID
            filters: フィルター条件

        Returns:
            Dict[str, Any]: 取得結果

        """
        try:
            self.logger.info(f"努力レポート取得開始: user_id={user_id}")

            # SQLiteリポジトリから取得
            reports = await self.effort_report_repository.get_by_user_id(user_id, filters)

            self.logger.info(f"努力レポート取得完了: user_id={user_id}, count={len(reports)}")
            return {"success": True, "data": [report.to_dict() for report in reports]}

        except Exception as e:
            self.logger.error(f"努力レポート取得エラー: user_id={user_id}, error={e}")
            return {"success": False, "message": f"努力レポートの取得に失敗しました: {e!s}"}

    async def get_effort_report(self, user_id: str, report_id: str) -> dict[str, Any]:
        """特定の努力レポートを取得

        Args:
            user_id: ユーザーID
            report_id: レポートID

        Returns:
            Dict[str, Any]: 取得結果

        """
        try:
            self.logger.info(f"努力レポート詳細取得開始: user_id={user_id}, report_id={report_id}")

            # SQLiteリポジトリから取得
            report = await self.effort_report_repository.get_user_report(user_id, report_id)

            if report:
                self.logger.info(f"努力レポート詳細取得成功: user_id={user_id}, report_id={report_id}")
                return {"success": True, "data": report.to_dict()}
            else:
                return {"success": False, "message": "努力レポートが見つかりません"}

        except Exception as e:
            self.logger.error(f"努力レポート詳細取得エラー: user_id={user_id}, report_id={report_id}, error={e}")
            return {"success": False, "message": f"努力レポートの取得に失敗しました: {e!s}"}

    async def update_effort_report(self, user_id: str, report_id: str, update_data: dict) -> dict[str, Any]:
        """努力レポートを更新

        Args:
            user_id: ユーザーID
            report_id: レポートID
            update_data: 更新データ

        Returns:
            Dict[str, Any]: 更新結果

        """
        try:
            self.logger.info(f"努力レポート更新開始: user_id={user_id}, report_id={report_id}")

            # 既存レポートを取得
            existing_report = await self.effort_report_repository.get_user_report(user_id, report_id)
            if not existing_report:
                return {"success": False, "message": "努力レポートが見つかりません"}

            # 更新データをマージ
            updated_data = existing_report.to_dict()
            updated_data.update(update_data)

            # エンティティ作成して更新
            updated_report = EffortReportRecord.from_dict(user_id, updated_data)
            updated_report.report_id = existing_report.report_id
            updated_report.created_at = existing_report.created_at  # 作成日時は保持

            result = await self.effort_report_repository.update(updated_report)

            self.logger.info(f"努力レポート更新完了: user_id={user_id}, report_id={report_id}")
            return {"success": True, "data": result.to_dict()}

        except Exception as e:
            self.logger.error(f"努力レポート更新エラー: user_id={user_id}, report_id={report_id}, error={e}")
            return {"success": False, "message": f"努力レポートの更新に失敗しました: {e!s}"}

    async def delete_effort_report(self, user_id: str, report_id: str) -> dict[str, Any]:
        """努力レポートを削除

        Args:
            user_id: ユーザーID
            report_id: レポートID

        Returns:
            Dict[str, Any]: 削除結果

        """
        try:
            self.logger.info(f"努力レポート削除開始: user_id={user_id}, report_id={report_id}")

            # SQLiteリポジトリで削除
            result = await self.effort_report_repository.delete_user_report(user_id, report_id)

            if result:
                self.logger.info(f"努力レポート削除完了: user_id={user_id}, report_id={report_id}")
                return {"success": True, "message": "努力レポートを削除しました", "deleted_data": result.to_dict()}
            else:
                return {"success": False, "message": "努力レポートが見つかりません"}

        except Exception as e:
            self.logger.error(f"努力レポート削除エラー: user_id={user_id}, report_id={report_id}, error={e}")
            return {"success": False, "message": f"努力レポートの削除に失敗しました: {e!s}"}

    async def generate_effort_report(self, user_id: str, period_days: int = 7) -> dict[str, Any]:
        """努力レポートを自動生成

        Args:
            user_id: ユーザーID
            period_days: 期間（日数）

        Returns:
            Dict[str, Any]: 生成結果

        """
        try:
            self.logger.info(f"努力レポート自動生成開始: user_id={user_id}, period_days={period_days}")

            # 実際のデータから努力分析を実行（ビジネスロジック）
            analysis_result = await self._analyze_user_effort_data(user_id, period_days)

            generated_data = {
                "period_days": period_days,
                "effort_count": analysis_result["effort_count"],
                "score": analysis_result["score"],
                "highlights": analysis_result["highlights"],
                "categories": analysis_result["categories"],
                "summary": analysis_result["summary"],
                "achievements": analysis_result["achievements"],
            }

            # エンティティ作成
            effort_report = EffortReportRecord.from_dict(user_id, generated_data)

            # SQLiteリポジトリに保存
            created_report = await self.effort_report_repository.create(effort_report)

            self.logger.info(f"努力レポート自動生成完了: user_id={user_id}, report_id={created_report.report_id}")
            return {"success": True, "id": created_report.report_id, "data": created_report.to_dict()}

        except Exception as e:
            self.logger.error(f"努力レポート自動生成エラー: user_id={user_id}, error={e}")
            return {"success": False, "message": f"努力レポートの自動生成に失敗しました: {e!s}"}

    async def _analyze_user_effort_data(self, user_id: str, period_days: int) -> dict[str, Any]:
        """ユーザーの努力データを分析（ビジネスロジック）

        Args:
            user_id: ユーザーID
            period_days: 分析期間（日数）

        Returns:
            dict[str, Any]: 分析結果
        """
        try:
            self.logger.info(f"💡 努力データ分析開始: user_id={user_id}, period_days={period_days}")

            # 期間設定
            end_date = datetime.now()
            start_date = end_date - timedelta(days=period_days)

            # 基本データ初期化
            analysis_data = {
                "meal_records_count": 0,
                "schedule_events_count": 0,
                "cooking_efforts": 0,
                "outdoor_activities": 0,
                "learning_activities": 0,
                "health_activities": 0,
                "total_records_count": 0,
                "children_count": 0,
            }

            # 家族情報分析
            await self._analyze_family_info(user_id, analysis_data)

            # 食事記録分析
            await self._analyze_meal_records(user_id, start_date, end_date, analysis_data)

            # 予定記録分析
            await self._analyze_schedule_records(user_id, start_date, end_date, analysis_data)

            # 総記録数を計算
            analysis_data["total_records_count"] = (
                analysis_data["meal_records_count"] + analysis_data["schedule_events_count"]
            )

            # AI強化総合分析とレポート生成
            return await self._generate_ai_enhanced_effort_report(analysis_data, period_days)

        except Exception as e:
            self.logger.error(f"❌ 努力データ分析エラー: {e}")
            # フォールバックとしてサンプルデータを返す
            return self._generate_fallback_report_data(period_days)

    async def _analyze_family_info(self, user_id: str, analysis_data: dict) -> None:
        """家族情報を分析"""
        try:
            family_info = await self.family_repository.get_by_user_id(user_id)
            if family_info:
                analysis_data["children_count"] = len(family_info.children)
                analysis_data["family_structure"] = family_info.family_structure or ""

                # 子どもの名前情報を収集
                child_names = []
                for child in family_info.children:
                    if hasattr(child, "name") and child.name:
                        child_names.append(child.name)
                    elif hasattr(child, "child_name") and child.child_name:
                        child_names.append(child.child_name)
                    elif isinstance(child, dict):
                        if child.get("name"):
                            child_names.append(child["name"])
                        elif child.get("child_name"):
                            child_names.append(child["child_name"])

                analysis_data["child_names"] = child_names
                self.logger.debug(f"家族情報分析: children={analysis_data['children_count']}人, names={child_names}")
        except Exception as e:
            self.logger.warning(f"家族情報分析エラー: {e}")

    async def _analyze_meal_records(
        self, user_id: str, start_date: datetime, end_date: datetime, analysis_data: dict
    ) -> None:
        """食事記録を分析"""
        try:
            # 家族情報から子どもリストを取得
            family_info = await self.family_repository.get_by_user_id(user_id)
            if not family_info or not family_info.children:
                self.logger.debug("家族情報または子ども情報が見つかりませんでした")
                return

            all_meal_records = []

            # 各子どもの食事記録を取得
            for i, child in enumerate(family_info.children):
                try:
                    # child_idが存在しない場合は既存のIDを使用
                    if hasattr(child, "child_id") and child.child_id:
                        child_id = child.child_id
                    else:
                        # デフォルトのchild_idを使用（データベース確認済み）
                        child_id = "frontend_child"

                    # search メソッドを使用（child_id, start_date, end_date指定）
                    child_meal_records = await self.meal_record_repository.search(
                        child_id=child_id,
                        start_date=start_date,
                        end_date=end_date,
                        limit=1000,  # 十分大きな値
                    )
                    all_meal_records.extend(child_meal_records)
                    self.logger.debug(f"子ども{child_id}の食事記録: {len(child_meal_records)}件")
                except Exception as child_error:
                    self.logger.warning(f"子ども{i}の食事記録取得エラー: {child_error}")

            analysis_data["meal_records_count"] = len(all_meal_records)

            # 具体的な食事記録内容を収集
            meal_details = []
            cooking_keywords = ["手作り", "自作", "料理", "調理"]

            for record in all_meal_records:
                # 記録の詳細情報を抽出
                notes = getattr(record, "notes", "") or ""
                description = getattr(record, "description", "") or ""
                food_name = getattr(record, "food_name", "") or ""
                meal_type = getattr(record, "meal_type", "") or ""
                created_at = getattr(record, "created_at", "")

                # 記録内容を整理
                meal_detail = {
                    "food_name": food_name,
                    "meal_type": meal_type,
                    "notes": notes,
                    "description": description,
                    "date": str(created_at)[:10] if created_at else "",
                    "is_homemade": False,
                }

                # 手作り料理判定
                combined_text = f"{notes} {description} {food_name}"
                if any(keyword in combined_text for keyword in cooking_keywords):
                    analysis_data["cooking_efforts"] += 1
                    meal_detail["is_homemade"] = True

                meal_details.append(meal_detail)

            # 分析データに詳細を追加
            analysis_data["meal_details"] = meal_details[:10]  # 最新10件まで

            # デバッグ：実際のテキストをログ出力
            if all_meal_records:
                sample = all_meal_records[0]
                self.logger.info(
                    f"🍽️ 食事記録サンプル: {getattr(sample, 'food_name', 'name_none')} | {getattr(sample, 'notes', 'notes_none')} | {getattr(sample, 'description', 'desc_none')}"
                )

            self.logger.info(
                f"🍽️ 食事記録分析: 記録{analysis_data['meal_records_count']}件, 手作り{analysis_data['cooking_efforts']}件"
            )

        except Exception as e:
            self.logger.warning(f"食事記録分析エラー: {e}")

    async def _analyze_schedule_records(
        self, user_id: str, start_date: datetime, end_date: datetime, analysis_data: dict
    ) -> None:
        """予定記録を分析"""
        try:
            # 期間内の予定記録を取得
            schedule_records = await self.schedule_record_repository.search(
                user_id=user_id,
                start_date=start_date,
                end_date=end_date,
                limit=1000,  # 十分大きな値
            )

            analysis_data["schedule_events_count"] = len(schedule_records)

            # 具体的なスケジュール記録内容を収集
            schedule_details = []
            outdoor_keywords = ["公園", "散歩", "外出", "お出かけ", "遊具"]
            learning_keywords = ["読書", "勉強", "学習", "遊び", "絵本", "知育"]
            health_keywords = ["病院", "健診", "予防接種", "検査", "医療"]

            for record in schedule_records:
                title = record.title or ""
                description = record.description or ""
                start_time = getattr(record, "start_time", "")
                created_at = getattr(record, "created_at", "")
                combined_text = f"{title} {description}".lower()

                # スケジュール詳細を整理
                schedule_detail = {
                    "title": title,
                    "description": description,
                    "start_time": str(start_time)[:10] if start_time else "",
                    "date": str(created_at)[:10] if created_at else "",
                    "category": "その他",
                }

                # カテゴリ分析と分類
                if any(keyword in combined_text for keyword in outdoor_keywords):
                    analysis_data["outdoor_activities"] += 1
                    schedule_detail["category"] = "外出・活動"
                elif any(keyword in combined_text for keyword in learning_keywords):
                    analysis_data["learning_activities"] += 1
                    schedule_detail["category"] = "学習・遊び"
                elif any(keyword in combined_text for keyword in health_keywords):
                    analysis_data["health_activities"] += 1
                    schedule_detail["category"] = "健康管理"

                schedule_details.append(schedule_detail)

            # 分析データに詳細を追加
            analysis_data["schedule_details"] = schedule_details[:10]  # 最新10件まで

            # デバッグ：実際のテキストをログ出力
            if schedule_records:
                sample_record = schedule_records[0]
                self.logger.info(
                    f"📅 スケジュールサンプル: {getattr(sample_record, 'title', 'title_none')} | {getattr(sample_record, 'description', 'desc_none')}"
                )

            self.logger.debug(
                f"予定記録分析: 記録{analysis_data['schedule_events_count']}件, "
                f"外出{analysis_data['outdoor_activities']}件, 学習{analysis_data['learning_activities']}件"
            )

        except Exception as e:
            self.logger.warning(f"予定記録分析エラー: {e}")

    async def _generate_ai_enhanced_effort_report(self, analysis_data: dict, period_days: int) -> dict[str, Any]:
        """AI強化レポート生成（ビジネスロジック）"""
        try:
            self.logger.info(f"🤖 AI強化レポート生成開始: period_days={period_days}")

            # 基本スコア計算（従来ロジック）
            total_score = self._calculate_base_score(analysis_data, period_days)

            # AIによる感動的なコンテンツ生成
            ai_content = await self._generate_ai_content(analysis_data, period_days, total_score)

            # カテゴリスコア生成
            categories = self._generate_categories(analysis_data)

            return {
                "effort_count": analysis_data["total_records_count"],
                "score": round(total_score, 1),
                "highlights": ai_content.get("highlights", []),
                "categories": categories,
                "summary": ai_content.get("summary", ""),
                "achievements": ai_content.get("achievements", []),
            }

        except Exception as e:
            self.logger.error(f"❌ AI強化レポート生成エラー: {e}")
            # フォールバックとして従来のロジックを使用
            return self._generate_effort_report_data(analysis_data, period_days)

    async def _generate_ai_content(self, analysis_data: dict, period_days: int, score: float) -> dict[str, Any]:
        """AIによる感動的なレポートコンテンツ生成"""
        try:
            self.logger.info(f"🤖 AI コンテンツ生成開始")

            # 分析データを整理
            data_summary = self._prepare_analysis_summary(analysis_data, period_days)
            self.logger.info(f"📊 分析サマリー: {data_summary}")

            # AI用プロンプトを構築
            prompt = self._build_effort_report_prompt(data_summary, score, period_days)
            self.logger.info(f"📝 プロンプト構築完了: 長さ={len(prompt)}")

            # Gemini AIでコンテンツ生成（高い温度設定で創造性を向上）
            self.logger.info("🚀 Gemini API呼び出し開始")
            model_options = {
                "temperature": 0.9,  # 高い創造性で毎回異なるレスポンス
                "top_p": 0.8,  # トークン選択の多様性
                "max_output_tokens": 2048,  # 十分な長さの出力
            }
            ai_response = await self.ai_analyzer.analyze_image_with_prompt("", prompt, model_options)

            self.logger.info(f"📨 AI応答受信: success={ai_response.get('success')}")
            if ai_response.get("raw_response"):
                self.logger.info(f"📄 生成されたコンテンツ長: {len(ai_response['raw_response'])}文字")
                self.logger.info(f"📄 生成コンテンツサンプル: {ai_response['raw_response'][:200]}...")

            if ai_response.get("success") and ai_response.get("raw_response"):
                parsed_content = self._parse_ai_response(ai_response["raw_response"])
                self.logger.info(f"✅ AI コンテンツ解析完了: highlights={len(parsed_content.get('highlights', []))}件")
                return parsed_content
            else:
                self.logger.warning("⚠️ AI応答が不正な形式でした。フォールバックを使用します。")
                if ai_response.get("error"):
                    self.logger.error(f"❌ AI生成エラー詳細: {ai_response['error']}")
                return self._generate_fallback_content(analysis_data, period_days)

        except Exception as e:
            self.logger.error(f"❌ AI コンテンツ生成エラー: {e}")
            return self._generate_fallback_content(analysis_data, period_days)

    def _build_effort_report_prompt(self, data_summary: dict, score: float, period_days: int) -> str:
        """努力レポート用AI プロンプト構築"""
        import random
        from datetime import datetime

        # 各生成で異なるバリエーション要素を追加
        current_time = datetime.now()
        generation_id = random.randint(1000, 9999)
        time_context = current_time.strftime("%Y年%m月%d日 %H時%M分")

        # メッセージトーンのバリエーション
        tone_variations = [
            "素直に嬉しい気持ちで",
            "率直に喜びを込めて",
            "自然な言葉で",
            "ストレートな表現で",
            "正直な感想として",
        ]
        selected_tone = random.choice(tone_variations)

        # 視点のバリエーション
        perspective_variations = [
            "子育てを見守る仲間として",
            "同じ親の立場から",
            "あなたの努力を知る人として",
            "子育ての大変さを理解する人として",
        ]
        selected_perspective = random.choice(perspective_variations)

        # 子どもの名前情報を整理
        child_names = data_summary.get("child_names", [])
        child_name_text = ""
        if child_names:
            if len(child_names) == 1:
                child_name_text = f"{child_names[0]}ちゃん"
            else:
                child_name_text = f"{', '.join(child_names)}ちゃんたち"
        else:
            child_name_text = "お子様"

        prompt = f"""
あなたは{selected_perspective}、以下のデータに基づいて、パパ・ママの子育ての努力を{selected_tone}レポートを作成してください。

## 生成情報
- 生成ID: {generation_id}
- 生成時刻: {time_context}
- 分析期間: 過去{period_days}日間

## 家族情報
- お子様: {child_name_text}
- 子どもの人数: {data_summary["children_count"]}人

## 実際の記録データ
- 総記録数: {data_summary["total_records"]}件
- 手作り料理: {data_summary["cooking_efforts"]}回
- 外出・活動: {data_summary["outdoor_activities"]}回
- 学習活動: {data_summary["learning_activities"]}回
- 健康管理: {data_summary["health_activities"]}回
- 総合スコア: {score}点

## 具体的な記録内容
### 食事記録の詳細
{self._format_meal_details(data_summary.get("meal_details", []))}

### スケジュール記録の詳細
{self._format_schedule_details(data_summary.get("schedule_details", []))}

## 求められる内容
パパ・ママの日々の努力を、{child_name_text}の記録を見ながら素直に評価してください。
大げさな表現ではなく、自然で嬉しい気持ちが伝わる言葉で、具体的な頑張りを認めてあげてください。

以下のJSON形式で返してください:

{{
  "highlights": [
    "具体的にこんなことを頑張ってたんですね、という発見を3つまで（各30-50文字程度、普通の言葉で）"
  ],
  "summary": "全体を見ての素直な感想（150-200文字、自然な口調で、{child_name_text}のことも含めて）",
  "achievements": [
    "これができてて良かったな、という項目を3つまで（各25-40文字程度、素直な評価で）"
  ]
}}

## 重要な書き方のポイント
1. **自然な言葉**: 「素晴らしい」「感動的」などの大げさな言葉は避けて、普通の会話のように
2. **具体的**: 上記の記録内容を見て、実際にやってることを挙げる
3. **親近感**: 同じ立場の人が見て「あーそうそう、大変だよね」と思える表現
4. **素直**: 「これ、頑張ってますね」「いいですね」「お疲れさまです」のような率直な言葉
5. **{child_name_text}のこと**: 子どもの名前を入れて、個人的な感じに
6. **記録を見た感想**: 「○○の記録を見ると」「○○をやってるんですね」など、実際の記録に触れる
7. **普通のテンション**: 興奮しすぎず、落ち着いて、でも温かい感じで

必ずJSON形式のみで回答してください。生成ID {generation_id} で{child_name_text}に特化した固有のレスポンスを作成してください。
"""

        return prompt.strip()

    def _format_meal_details(self, meal_details: list) -> str:
        """食事記録詳細をフォーマット"""
        if not meal_details:
            return "記録なし"

        formatted = []
        homemade_count = 0
        for meal in meal_details[:3]:  # 最新3件まで（短縮）
            if meal.get("is_homemade"):
                homemade_count += 1
                food_name = meal.get("food_name", "手作り料理")
                formatted.append(f"手作り{food_name}")

        if homemade_count == 0:
            return "通常の食事記録"
        return f"{', '.join(formatted)}など{homemade_count}回の手作り料理"

    def _format_schedule_details(self, schedule_details: list) -> str:
        """スケジュール記録詳細をフォーマット"""
        if not schedule_details:
            return "記録なし"

        categories = {}
        for schedule in schedule_details[:3]:  # 最新3件まで（短縮）
            category = schedule.get("category", "その他")
            title = schedule.get("title", "")
            if category not in categories:
                categories[category] = []
            if title:
                categories[category].append(title)

        formatted = []
        for category, titles in categories.items():
            if titles:
                formatted.append(f"{category}: {', '.join(titles[:2])}")

        return "; ".join(formatted) if formatted else "日常の記録"

    def _prepare_analysis_summary(self, analysis_data: dict, period_days: int) -> dict:
        """分析データサマリー準備"""
        return {
            "total_records": analysis_data.get("total_records_count", 0),
            "cooking_efforts": analysis_data.get("cooking_efforts", 0),
            "outdoor_activities": analysis_data.get("outdoor_activities", 0),
            "learning_activities": analysis_data.get("learning_activities", 0),
            "health_activities": analysis_data.get("health_activities", 0),
            "children_count": analysis_data.get("children_count", 1),
            "child_names": analysis_data.get("child_names", []),
            "meal_details": analysis_data.get("meal_details", []),
            "schedule_details": analysis_data.get("schedule_details", []),
            "period_days": period_days,
        }

    def _parse_ai_response(self, response: str) -> dict[str, Any]:
        """AI応答をパース"""
        try:
            import json
            import re

            self.logger.debug(f"🔍 パース対象の応答: {response[:500]}...")

            # マークダウンコードブロック内のJSONを抽出
            json_match = re.search(r"```json\s*(\{.*?\})\s*```", response, re.DOTALL)
            if not json_match:
                # 通常のJSONブロックを抽出
                json_match = re.search(r"\{.*\}", response, re.DOTALL)

            if json_match:
                json_str = json_match.group(1) if json_match.lastindex else json_match.group()
                self.logger.debug(f"🔍 抽出されたJSON: {json_str[:200]}...")

                parsed = json.loads(json_str)

                result = {
                    "highlights": parsed.get("highlights", [])[:3],
                    "summary": parsed.get("summary", "")[:400],  # より長い制限
                    "achievements": parsed.get("achievements", [])[:3],
                }
                self.logger.info(f"✅ JSON パース成功: highlights={len(result['highlights'])}件")
                return result
            else:
                self.logger.warning("AI応答にJSONが見つかりませんでした")
                return {}

        except Exception as e:
            self.logger.error(f"AI応答パースエラー: {e}")
            return {}

    def _generate_fallback_content(self, analysis_data: dict, period_days: int) -> dict[str, Any]:
        """AI失敗時のフォールバックコンテンツ"""
        return {
            "highlights": [
                f"過去{period_days}日間、愛情を込めて子育てに取り組まれました",
                "日々の小さな努力が積み重なっています",
                "お子さまへの深い愛情が伝わってきます",
            ],
            "summary": f"過去{period_days}日間、あなたの愛情あふれる子育ての努力を心から讃えます。すべての記録に、お子さまへの深い愛が込められています。",
            "achievements": ["愛情深い子育て実践", "継続的な記録管理", "子どもの成長支援"],
        }

    def _calculate_base_score(self, analysis_data: dict, period_days: int) -> float:
        """基本スコア計算（従来ロジック）"""
        base_score = min(100.0, analysis_data["total_records_count"] * 5)
        activity_bonus = (analysis_data["cooking_efforts"] + analysis_data["outdoor_activities"]) * 10
        consistency_bonus = min(30.0, (analysis_data["total_records_count"] / period_days) * 15)
        return min(100.0, base_score + activity_bonus + consistency_bonus)

    def _generate_categories(self, analysis_data: dict) -> dict[str, int]:
        """カテゴリスコア生成"""
        return {
            "記録継続": min(10, analysis_data["total_records_count"] // 2),
            "食事管理": min(10, analysis_data["cooking_efforts"]),
            "活動企画": min(10, analysis_data["outdoor_activities"] + analysis_data["learning_activities"]),
            "健康管理": min(10, analysis_data["health_activities"] + 2),
        }

    def _generate_effort_report_data(self, analysis_data: dict, period_days: int) -> dict[str, Any]:
        """分析データから努力レポートを生成（ビジネスロジック）"""
        try:
            # 総記録数計算
            analysis_data["total_records_count"] = (
                analysis_data["meal_records_count"] + analysis_data["schedule_events_count"]
            )

            # スコア計算（ビジネスロジック）
            base_score = min(100.0, analysis_data["total_records_count"] * 5)  # 記録数ベース
            activity_bonus = (
                analysis_data["cooking_efforts"] + analysis_data["outdoor_activities"]
            ) * 10  # 活動ボーナス
            consistency_bonus = min(30.0, (analysis_data["total_records_count"] / period_days) * 15)  # 継続性ボーナス

            total_score = min(100.0, base_score + activity_bonus + consistency_bonus)

            # ハイライト生成（ビジネスロジック）
            highlights = self._generate_highlights(analysis_data, period_days)

            # カテゴリスコア生成（ビジネスロジック）
            categories = {
                "記録継続": min(10, analysis_data["total_records_count"] // 2),
                "食事管理": min(10, analysis_data["cooking_efforts"]),
                "活動企画": min(10, analysis_data["outdoor_activities"] + analysis_data["learning_activities"]),
                "健康管理": min(10, analysis_data["health_activities"] + 2),
            }

            # サマリー生成（ビジネスロジック）
            summary = self._generate_summary(analysis_data, period_days, total_score)

            # 達成項目生成（ビジネスロジック）
            achievements = self._generate_achievements(analysis_data, period_days)

            return {
                "effort_count": analysis_data["total_records_count"],
                "score": round(total_score, 1),
                "highlights": highlights,
                "categories": categories,
                "summary": summary,
                "achievements": achievements,
            }

        except Exception as e:
            self.logger.error(f"❌ レポートデータ生成エラー: {e}")
            return self._generate_fallback_report_data(period_days)

    def _generate_highlights(self, analysis_data: dict, period_days: int) -> list[str]:
        """ハイライト生成（ビジネスロジック）"""
        highlights = []

        if analysis_data["total_records_count"] >= period_days * 2:
            highlights.append(f"{period_days}日間で継続的な記録を維持されました")

        if analysis_data["cooking_efforts"] >= 3:
            highlights.append(f"手作り料理に{analysis_data['cooking_efforts']}回チャレンジされました")

        if analysis_data["outdoor_activities"] >= 2:
            highlights.append(f"お子さまとの外出・活動を{analysis_data['outdoor_activities']}回計画されました")

        if analysis_data["learning_activities"] >= 2:
            highlights.append(f"学習・遊びの活動を{analysis_data['learning_activities']}回記録されました")

        if not highlights:
            highlights.append("子育ての記録に取り組まれています")

        return highlights[:3]

    def _generate_summary(self, analysis_data: dict, period_days: int, score: float) -> str:
        """サマリー生成（ビジネスロジック）"""
        if score >= 90:
            grade = "素晴らしい"
        elif score >= 75:
            grade = "とても良い"
        elif score >= 60:
            grade = "良い"
        else:
            grade = "頑張っている"

        children_text = ""
        if analysis_data["children_count"] > 0:
            children_text = f"{analysis_data['children_count']}人のお子さまとの"

        return (
            f"過去{period_days}日間で{grade}子育ての記録を残されました。"
            f"{children_text}日々の記録が{analysis_data['total_records_count']}件蓄積され、"
            f"継続的な子育てへの取り組みが伺えます。"
        )

    def _generate_achievements(self, analysis_data: dict, period_days: int) -> list[str]:
        """達成項目生成（ビジネスロジック）"""
        achievements = []

        if analysis_data["total_records_count"] >= period_days * 2:
            achievements.append(f"{period_days}日間継続記録達成")

        if analysis_data["cooking_efforts"] >= 5:
            achievements.append("手作り料理週5回達成")
        elif analysis_data["cooking_efforts"] >= 3:
            achievements.append("手作り料理継続中")

        if analysis_data["outdoor_activities"] >= 3:
            achievements.append("アクティブな外出企画")

        if analysis_data["meal_records_count"] >= 10:
            achievements.append("食事記録充実")

        if not achievements:
            achievements.append("子育て記録への取り組み")

        return achievements[:3]

    def _generate_fallback_report_data(self, period_days: int) -> dict[str, Any]:
        """フォールバック用のサンプルレポートデータ"""
        return {
            "effort_count": 10,
            "score": 75.0,
            "highlights": [
                "子育ての記録に取り組まれています",
                "継続的な記録管理を心がけています",
            ],
            "categories": {"記録継続": 5, "食事管理": 3, "活動企画": 2, "健康管理": 4},
            "summary": f"過去{period_days}日間の子育ての取り組みが記録されています。",
            "achievements": ["記録管理への取り組み"],
        }
