"""成長記録管理ツール - Genius Agents統合

Agentsが成長記録の作成・編集・削除・分析を行えるツール
"""

import logging
from datetime import datetime
from typing import Any

from google.ai.generativelanguage_v1beta.types import FunctionDeclaration, Schema, Type

from src.application.usecases.growth_record_usecase import GrowthRecordUseCase


class GrowthRecordTool:
    """成長記録管理ツール
    
    Genius Agentsが成長記録の作成、編集、削除、分析を行うためのツール
    """

    def __init__(
        self,
        growth_record_usecase: GrowthRecordUseCase,
        logger: logging.Logger,
    ):
        self.growth_record_usecase = growth_record_usecase
        self.logger = logger

    def get_function_declarations(self) -> list[FunctionDeclaration]:
        """成長記録管理用のFunctionDeclarationを取得"""
        return [
            # 成長記録作成
            FunctionDeclaration(
                name="create_growth_record",
                description="新しい成長記録を作成します。身長・体重の記録から、言葉の発達、できるようになったことまで幅広く記録できます。",
                parameters=Schema(
                    type=Type.OBJECT,
                    properties={
                        "user_id": Schema(type=Type.STRING, description="ユーザーID"),
                        "child_name": Schema(type=Type.STRING, description="お子さんの名前"),
                        "title": Schema(type=Type.STRING, description="記録のタイトル"),
                        "description": Schema(type=Type.STRING, description="記録の詳細説明"),
                        "date": Schema(type=Type.STRING, description="記録日付（YYYY-MM-DD形式、省略時は今日）"),
                        "type": Schema(
                            type=Type.STRING,
                            description="成長記録のタイプ",
                            enum=["body_growth", "language_growth", "skills", "social_skills", "hobbies", "life_skills", "milestone", "photo"],
                        ),
                        "category": Schema(type=Type.STRING, description="詳細カテゴリ（任意）"),
                        "value": Schema(type=Type.STRING, description="測定値（身長・体重など、任意）"),
                        "unit": Schema(type=Type.STRING, description="単位（cm、kg、回など、任意）"),
                        "detected_by": Schema(
                            type=Type.STRING,
                            description="記録者",
                            enum=["genie", "parent"],
                        ),
                    },
                    required=["user_id", "child_name", "title", "description", "type"],
                ),
            ),

            # 成長記録一覧取得
            FunctionDeclaration(
                name="get_growth_records",
                description="成長記録の一覧を取得します。子どもや記録タイプで絞り込み検索ができます。",
                parameters=Schema(
                    type=Type.OBJECT,
                    properties={
                        "user_id": Schema(type=Type.STRING, description="ユーザーID"),
                        "child_name": Schema(type=Type.STRING, description="お子さんの名前でフィルタ（任意）"),
                        "type": Schema(
                            type=Type.STRING,
                            description="記録タイプでフィルタ（任意）",
                            enum=["all", "body_growth", "language_growth", "skills", "social_skills", "hobbies", "life_skills", "milestone", "photo"],
                        ),
                        "category": Schema(type=Type.STRING, description="カテゴリでフィルタ（任意）"),
                        "limit": Schema(type=Type.NUMBER, description="取得件数上限（デフォルト10件）"),
                    },
                    required=["user_id"],
                ),
            ),

            # 特定の成長記録取得
            FunctionDeclaration(
                name="get_growth_record",
                description="指定したIDの成長記録の詳細を取得します。",
                parameters=Schema(
                    type=Type.OBJECT,
                    properties={
                        "user_id": Schema(type=Type.STRING, description="ユーザーID"),
                        "record_id": Schema(type=Type.STRING, description="取得する成長記録のID"),
                    },
                    required=["user_id", "record_id"],
                ),
            ),

            # 成長記録更新
            FunctionDeclaration(
                name="update_growth_record",
                description="既存の成長記録を更新します。タイトル、説明、測定値などを修正できます。",
                parameters=Schema(
                    type=Type.OBJECT,
                    properties={
                        "user_id": Schema(type=Type.STRING, description="ユーザーID"),
                        "record_id": Schema(type=Type.STRING, description="更新する成長記録のID"),
                        "title": Schema(type=Type.STRING, description="新しいタイトル（任意）"),
                        "description": Schema(type=Type.STRING, description="新しい説明（任意）"),
                        "date": Schema(type=Type.STRING, description="新しい記録日付（任意）"),
                        "type": Schema(
                            type=Type.STRING,
                            description="新しい記録タイプ（任意）",
                            enum=["body_growth", "language_growth", "skills", "social_skills", "hobbies", "life_skills", "milestone", "photo"],
                        ),
                        "category": Schema(type=Type.STRING, description="新しいカテゴリ（任意）"),
                        "value": Schema(type=Type.STRING, description="新しい測定値（任意）"),
                        "unit": Schema(type=Type.STRING, description="新しい単位（任意）"),
                    },
                    required=["user_id", "record_id"],
                ),
            ),

            # 成長記録削除
            FunctionDeclaration(
                name="delete_growth_record",
                description="不要になった成長記録を削除します。",
                parameters=Schema(
                    type=Type.OBJECT,
                    properties={
                        "user_id": Schema(type=Type.STRING, description="ユーザーID"),
                        "record_id": Schema(type=Type.STRING, description="削除する成長記録のID"),
                    },
                    required=["user_id", "record_id"],
                ),
            ),

            # 成長分析
            FunctionDeclaration(
                name="analyze_growth_progress",
                description="お子さんの成長記録を分析して、成長の傾向や次のマイルストーンを提案します。",
                parameters=Schema(
                    type=Type.OBJECT,
                    properties={
                        "user_id": Schema(type=Type.STRING, description="ユーザーID"),
                        "child_name": Schema(type=Type.STRING, description="お子さんの名前"),
                        "analysis_type": Schema(
                            type=Type.STRING,
                            description="分析タイプ",
                            enum=["overall", "body_growth", "language_growth", "skills", "milestone_prediction"],
                        ),
                        "period_months": Schema(type=Type.NUMBER, description="分析対象期間（月数、デフォルト3ヶ月）"),
                    },
                    required=["user_id", "child_name"],
                ),
            ),
        ]

    async def execute_function(self, function_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        """成長記録管理関数を実行"""
        try:
            self.logger.info(f"成長記録ツール実行: {function_name} with args: {arguments}")

            if function_name == "create_growth_record":
                return await self._create_growth_record(arguments)
            elif function_name == "get_growth_records":
                return await self._get_growth_records(arguments)
            elif function_name == "get_growth_record":
                return await self._get_growth_record(arguments)
            elif function_name == "update_growth_record":
                return await self._update_growth_record(arguments)
            elif function_name == "delete_growth_record":
                return await self._delete_growth_record(arguments)
            elif function_name == "analyze_growth_progress":
                return await self._analyze_growth_progress(arguments)
            else:
                raise ValueError(f"未知の関数: {function_name}")

        except Exception as e:
            error_msg = f"成長記録ツールエラー ({function_name}): {e}"
            self.logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "details": str(e),
            }

    async def _create_growth_record(self, args: dict[str, Any]) -> dict[str, Any]:
        """成長記録作成"""
        record_data = {
            "child_name": args["child_name"],
            "title": args["title"],
            "description": args["description"],
            "date": args.get("date", datetime.now().strftime("%Y-%m-%d")),
            "type": args["type"],
            "category": args.get("category", ""),
            "value": args.get("value", ""),
            "unit": args.get("unit", ""),
            "detected_by": args.get("detected_by", "genie"),
        }

        result = await self.growth_record_usecase.create_growth_record(args["user_id"], record_data)

        if result.get("success"):
            return {
                "success": True,
                "message": f"✅ {args['child_name']}さんの成長記録「{args['title']}」を保存しました！",
                "record_id": result.get("id"),
                "data": result.get("data"),
            }
        else:
            return {
                "success": False,
                "error": result.get("message", "成長記録の作成に失敗しました"),
            }

    async def _get_growth_records(self, args: dict[str, Any]) -> dict[str, Any]:
        """成長記録一覧取得"""
        filters = {}
        if args.get("child_name"):
            filters["child_name"] = args["child_name"]
        if args.get("type") and args["type"] != "all":
            filters["type"] = args["type"]
        if args.get("category"):
            filters["category"] = args["category"]

        result = await self.growth_record_usecase.get_growth_records(args["user_id"], filters)

        if result.get("success"):
            records = result.get("data", [])
            limit = args.get("limit", 10)
            limited_records = records[:limit] if records else []

            return {
                "success": True,
                "records": limited_records,
                "total_count": len(records),
                "showing_count": len(limited_records),
                "message": self._format_records_summary(limited_records, args.get("child_name")),
            }
        else:
            return {
                "success": False,
                "error": result.get("message", "成長記録の取得に失敗しました"),
            }

    async def _get_growth_record(self, args: dict[str, Any]) -> dict[str, Any]:
        """特定の成長記録取得"""
        result = await self.growth_record_usecase.get_growth_record(args["user_id"], args["record_id"])

        if result.get("success"):
            record = result.get("data")
            return {
                "success": True,
                "record": record,
                "message": self._format_single_record(record),
            }
        else:
            return {
                "success": False,
                "error": result.get("message", "成長記録が見つかりません"),
            }

    async def _update_growth_record(self, args: dict[str, Any]) -> dict[str, Any]:
        """成長記録更新"""
        update_data = {}
        for field in ["title", "description", "date", "type", "category", "value", "unit"]:
            if args.get(field):
                update_data[field] = args[field]

        if not update_data:
            return {
                "success": False,
                "error": "更新する内容が指定されていません",
            }

        result = await self.growth_record_usecase.update_growth_record(
            args["user_id"],
            args["record_id"],
            update_data,
        )

        if result.get("success"):
            return {
                "success": True,
                "message": f"✅ 成長記録を更新しました（ID: {args['record_id']}）",
                "data": result.get("data"),
            }
        else:
            return {
                "success": False,
                "error": result.get("message", "成長記録の更新に失敗しました"),
            }

    async def _delete_growth_record(self, args: dict[str, Any]) -> dict[str, Any]:
        """成長記録削除"""
        result = await self.growth_record_usecase.delete_growth_record(args["user_id"], args["record_id"])

        if result.get("success"):
            return {
                "success": True,
                "message": f"✅ 成長記録を削除しました（ID: {args['record_id']}）",
            }
        else:
            return {
                "success": False,
                "error": result.get("message", "成長記録の削除に失敗しました"),
            }

    async def _analyze_growth_progress(self, args: dict[str, Any]) -> dict[str, Any]:
        """成長分析"""
        # 対象期間の記録を取得
        filters = {"child_name": args["child_name"]}
        analysis_type = args.get("analysis_type", "overall")

        if analysis_type != "overall":
            filters["type"] = analysis_type

        result = await self.growth_record_usecase.get_growth_records(args["user_id"], filters)

        if not result.get("success"):
            return {
                "success": False,
                "error": "成長記録の取得に失敗しました",
            }

        records = result.get("data", [])
        analysis = self._perform_growth_analysis(records, analysis_type, args["child_name"])

        return {
            "success": True,
            "analysis": analysis,
            "records_analyzed": len(records),
            "message": analysis.get("summary", "成長分析を完了しました"),
        }

    def _perform_growth_analysis(self, records: list[dict], analysis_type: str, child_name: str) -> dict[str, Any]:
        """成長分析の実行"""
        if not records:
            return {
                "summary": f"{child_name}さんの記録がまだありません。記録を作成して成長を追跡しましょう！",
                "recommendations": ["定期的な身長・体重の記録", "マイルストーンの記録", "日常の成長の記録"],
            }

        # 最新の記録から分析
        recent_records = sorted(records, key=lambda x: x.get("date", ""), reverse=True)[:10]

        analysis = {
            "period": f"最新{len(recent_records)}件の記録を分析",
            "summary": "",
            "trends": [],
            "milestones": [],
            "recommendations": [],
        }

        if analysis_type == "body_growth":
            analysis.update(self._analyze_body_growth(recent_records, child_name))
        elif analysis_type == "language_growth":
            analysis.update(self._analyze_language_growth(recent_records, child_name))
        elif analysis_type == "skills":
            analysis.update(self._analyze_skills_development(recent_records, child_name))
        else:
            analysis.update(self._analyze_overall_growth(recent_records, child_name))

        return analysis

    def _analyze_body_growth(self, records: list[dict], child_name: str) -> dict[str, Any]:
        """身体成長分析"""
        body_records = [r for r in records if r.get("type") == "body_growth"]

        return {
            "summary": f"{child_name}さんの身体成長記録を{len(body_records)}件分析しました",
            "trends": ["順調な成長を続けています"] if body_records else ["身体測定の記録を開始しましょう"],
            "recommendations": [
                "定期的な身長・体重測定",
                "成長曲線との比較",
                "栄養バランスの確認",
            ],
        }

    def _analyze_language_growth(self, records: list[dict], child_name: str) -> dict[str, Any]:
        """言語発達分析"""
        language_records = [r for r in records if r.get("type") == "language_growth"]

        return {
            "summary": f"{child_name}さんの言語発達記録を{len(language_records)}件分析しました",
            "trends": ["言葉の発達が見られます"] if language_records else ["言葉の発達記録を始めましょう"],
            "recommendations": [
                "新しい言葉の記録",
                "読み聞かせの記録",
                "会話の内容記録",
            ],
        }

    def _analyze_skills_development(self, records: list[dict], child_name: str) -> dict[str, Any]:
        """スキル発達分析"""
        skill_records = [r for r in records if r.get("type") in ["skills", "social_skills", "life_skills"]]

        return {
            "summary": f"{child_name}さんのスキル発達記録を{len(skill_records)}件分析しました",
            "trends": ["新しいスキルを獲得しています"] if skill_records else ["スキル発達の記録を始めましょう"],
            "recommendations": [
                "できるようになったことの記録",
                "挑戦中のことの記録",
                "社会性の発達記録",
            ],
        }

    def _analyze_overall_growth(self, records: list[dict], child_name: str) -> dict[str, Any]:
        """総合成長分析"""
        type_counts = {}
        for record in records:
            record_type = record.get("type", "other")
            type_counts[record_type] = type_counts.get(record_type, 0) + 1

        return {
            "summary": f"{child_name}さんの総合成長記録を{len(records)}件分析しました",
            "trends": [f"{self._get_type_label(t)}: {c}件" for t, c in type_counts.items()],
            "recommendations": [
                "バランスの良い記録継続",
                "定期的な振り返り",
                "成長の可視化",
            ],
        }

    def _format_records_summary(self, records: list[dict], child_name_filter: str = "") -> str:
        """記録一覧の要約フォーマット"""
        if not records:
            filter_text = f"（{child_name_filter}さんの）" if child_name_filter else ""
            return f"📋 成長記録{filter_text}はまだありません。最初の記録を作成してみましょう！"

        summary_parts = []
        if child_name_filter:
            summary_parts.append(f"📊 {child_name_filter}さんの成長記録（{len(records)}件）:")
        else:
            summary_parts.append(f"📊 成長記録一覧（{len(records)}件）:")

        for i, record in enumerate(records[:5]):
            date = record.get("date", "")
            title = record.get("title", "")
            type_label = self._get_type_label(record.get("type", ""))
            summary_parts.append(f"  {i + 1}. {date} - {title} ({type_label})")

        if len(records) > 5:
            summary_parts.append(f"  ...他{len(records) - 5}件")

        return "\n".join(summary_parts)

    def _format_single_record(self, record: dict) -> str:
        """単一記録の詳細フォーマット"""
        if not record:
            return "記録が見つかりませんでした。"

        parts = [
            "📝 成長記録詳細",
            "",
            f"👶 お子さん: {record.get('child_name', '')}",
            f"📅 日付: {record.get('date', '')}",
            f"🏷️ タイトル: {record.get('title', '')}",
            f"📋 説明: {record.get('description', '')}",
            f"🎯 タイプ: {self._get_type_label(record.get('type', ''))}",
        ]

        if record.get("category"):
            parts.append(f"📂 カテゴリ: {record.get('category')}")

        if record.get("value") and record.get("unit"):
            parts.append(f"📏 測定値: {record.get('value')} {record.get('unit')}")

        parts.append(f"👤 記録者: {record.get('detected_by', 'unknown')}")

        return "\n".join(parts)

    def _get_type_label(self, record_type: str) -> str:
        """記録タイプのラベル変換"""
        type_labels = {
            "body_growth": "からだの成長",
            "language_growth": "ことばの成長",
            "skills": "できること",
            "social_skills": "お友達との関わり",
            "hobbies": "習い事・特技",
            "life_skills": "生活スキル",
            "milestone": "マイルストーン",
            "photo": "写真記録",
        }
        return type_labels.get(record_type, record_type)
