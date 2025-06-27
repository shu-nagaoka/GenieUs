"""予定管理ツール - Genius Agents統合

Agentsが予定の作成・編集・削除・リマインダーを行えるツール
"""

import logging
from datetime import datetime, timedelta
from typing import Any

from google.ai.generativelanguage_v1beta.types import FunctionDeclaration, Schema, Type

from src.application.usecases.schedule_management_usecase import (
    CreateScheduleRequest,
    ScheduleManagementUseCase,
    UpdateScheduleRequest,
)


class ScheduleTool:
    """予定管理ツール
    
    Genius Agentsが予定の作成、編集、削除、リマインダーを行うためのツール
    """

    def __init__(
        self,
        schedule_usecase: ScheduleManagementUseCase,
        logger: logging.Logger,
    ):
        self.schedule_usecase = schedule_usecase
        self.logger = logger

    def get_function_declarations(self) -> list[FunctionDeclaration]:
        """予定管理用のFunctionDeclarationを取得"""
        return [
            # 予定作成
            FunctionDeclaration(
                name="create_schedule",
                description="新しい予定を作成します。検診、お出かけ、習い事など様々な予定を管理できます。",
                parameters=Schema(
                    type=Type.OBJECT,
                    properties={
                        "user_id": Schema(type=Type.STRING, description="ユーザーID"),
                        "title": Schema(type=Type.STRING, description="予定のタイトル"),
                        "description": Schema(type=Type.STRING, description="予定の詳細説明"),
                        "start_datetime": Schema(type=Type.STRING, description="開始日時（ISO形式）"),
                        "end_datetime": Schema(type=Type.STRING, description="終了日時（ISO形式）"),
                        "event_type": Schema(
                            type=Type.STRING,
                            description="予定の種類",
                            enum=["medical", "outing", "school", "other"],
                        ),
                        "location": Schema(type=Type.STRING, description="場所"),
                        "notes": Schema(type=Type.STRING, description="メモ・注意点"),
                        "reminder_minutes": Schema(type=Type.NUMBER, description="リマインダー（分前）"),
                    },
                    required=["user_id", "title", "start_datetime", "event_type"],
                ),
            ),

            # 予定取得
            FunctionDeclaration(
                name="get_schedules",
                description="指定した期間の予定一覧を取得します。今日、今週、今月の予定を確認できます。",
                parameters=Schema(
                    type=Type.OBJECT,
                    properties={
                        "user_id": Schema(type=Type.STRING, description="ユーザーID"),
                        "start_date": Schema(type=Type.STRING, description="取得開始日（YYYY-MM-DD）"),
                        "end_date": Schema(type=Type.STRING, description="取得終了日（YYYY-MM-DD）"),
                        "event_type": Schema(
                            type=Type.STRING,
                            description="予定の種類でフィルタ（任意）",
                            enum=["medical", "outing", "school", "other"],
                        ),
                    },
                    required=["user_id"],
                ),
            ),

            # 予定更新
            FunctionDeclaration(
                name="update_schedule",
                description="既存の予定を更新します。時間変更、場所変更、詳細追加ができます。",
                parameters=Schema(
                    type=Type.OBJECT,
                    properties={
                        "user_id": Schema(type=Type.STRING, description="ユーザーID"),
                        "schedule_id": Schema(type=Type.STRING, description="更新する予定のID"),
                        "title": Schema(type=Type.STRING, description="新しいタイトル（任意）"),
                        "description": Schema(type=Type.STRING, description="新しい説明（任意）"),
                        "start_datetime": Schema(type=Type.STRING, description="新しい開始日時（任意）"),
                        "end_datetime": Schema(type=Type.STRING, description="新しい終了日時（任意）"),
                        "location": Schema(type=Type.STRING, description="新しい場所（任意）"),
                        "status": Schema(
                            type=Type.STRING,
                            description="予定の状態",
                            enum=["upcoming", "completed", "cancelled"],
                        ),
                        "notes": Schema(type=Type.STRING, description="新しいメモ（任意）"),
                    },
                    required=["user_id", "schedule_id"],
                ),
            ),

            # 予定削除
            FunctionDeclaration(
                name="delete_schedule",
                description="不要になった予定を削除します。",
                parameters=Schema(
                    type=Type.OBJECT,
                    properties={
                        "user_id": Schema(type=Type.STRING, description="ユーザーID"),
                        "schedule_id": Schema(type=Type.STRING, description="削除する予定のID"),
                    },
                    required=["user_id", "schedule_id"],
                ),
            ),

            # 今日の予定確認
            FunctionDeclaration(
                name="get_today_schedules",
                description="今日の予定を確認します。朝の確認や出かける前のチェックに便利です。",
                parameters=Schema(
                    type=Type.OBJECT,
                    properties={
                        "user_id": Schema(type=Type.STRING, description="ユーザーID"),
                    },
                    required=["user_id"],
                ),
            ),

            # 予定提案
            FunctionDeclaration(
                name="suggest_schedule",
                description="お子さんの成長段階に応じた予定（検診、遊び場、習い事など）を提案します。",
                parameters=Schema(
                    type=Type.OBJECT,
                    properties={
                        "user_id": Schema(type=Type.STRING, description="ユーザーID"),
                        "child_age_months": Schema(type=Type.NUMBER, description="お子さんの月齢"),
                        "interests": Schema(
                            type=Type.ARRAY,
                            description="お子さんの興味・関心",
                            items=Schema(type=Type.STRING),
                        ),
                        "available_days": Schema(
                            type=Type.ARRAY,
                            description="空いている曜日",
                            items=Schema(type=Type.STRING),
                        ),
                    },
                    required=["user_id", "child_age_months"],
                ),
            ),
        ]

    async def execute_function(self, function_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        """予定管理関数を実行"""
        try:
            self.logger.info(f"予定管理ツール実行: {function_name} with args: {arguments}")

            if function_name == "create_schedule":
                return await self._create_schedule(arguments)
            elif function_name == "get_schedules":
                return await self._get_schedules(arguments)
            elif function_name == "update_schedule":
                return await self._update_schedule(arguments)
            elif function_name == "delete_schedule":
                return await self._delete_schedule(arguments)
            elif function_name == "get_today_schedules":
                return await self._get_today_schedules(arguments)
            elif function_name == "suggest_schedule":
                return await self._suggest_schedule(arguments)
            else:
                raise ValueError(f"未知の関数: {function_name}")

        except Exception as e:
            error_msg = f"予定管理ツールエラー ({function_name}): {e}"
            self.logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "details": str(e),
            }

    async def _create_schedule(self, args: dict[str, Any]) -> dict[str, Any]:
        """予定作成"""
        request = CreateScheduleRequest(
            user_id=args["user_id"],
            title=args["title"],
            description=args.get("description", ""),
            start_datetime=args["start_datetime"],
            end_datetime=args.get("end_datetime"),
            event_type=args["event_type"],
            location=args.get("location", ""),
            notes=args.get("notes", ""),
            created_by="genie",  # AI作成として記録
        )

        response = await self.schedule_usecase.create_schedule(request)

        if response.success:
            return {
                "success": True,
                "message": "予定を作成しました",
                "schedule_id": response.schedule_id,
                "schedule": response.schedule.to_dict() if response.schedule else None,
            }
        else:
            return {
                "success": False,
                "error": response.error_message or "予定の作成に失敗しました",
            }

    async def _get_schedules(self, args: dict[str, Any]) -> dict[str, Any]:
        """予定一覧取得"""
        # デフォルトは今日から1週間後まで
        if "start_date" not in args:
            args["start_date"] = datetime.now().strftime("%Y-%m-%d")
        if "end_date" not in args:
            end_date = datetime.now() + timedelta(days=7)
            args["end_date"] = end_date.strftime("%Y-%m-%d")

        response = await self.schedule_usecase.get_schedules_by_date_range(
            args["user_id"],
            args["start_date"],
            args["end_date"],
        )

        if response.success:
            schedules_data = []
            for schedule in response.schedules:
                schedules_data.append(schedule.to_dict())

            return {
                "success": True,
                "schedules": schedules_data,
                "total_count": len(schedules_data),
                "period": f"{args['start_date']} から {args['end_date']}",
            }
        else:
            return {
                "success": False,
                "error": response.error_message or "予定一覧の取得に失敗しました",
            }

    async def _update_schedule(self, args: dict[str, Any]) -> dict[str, Any]:
        """予定更新"""
        request = UpdateScheduleRequest(
            user_id=args["user_id"],
            schedule_id=args["schedule_id"],
            title=args.get("title"),
            description=args.get("description"),
            start_datetime=args.get("start_datetime"),
            end_datetime=args.get("end_datetime"),
            location=args.get("location"),
            status=args.get("status"),
            notes=args.get("notes"),
        )

        response = await self.schedule_usecase.update_schedule(request)

        if response.success:
            return {
                "success": True,
                "message": "予定を更新しました",
                "schedule": response.schedule.to_dict() if response.schedule else None,
            }
        else:
            return {
                "success": False,
                "error": response.error_message or "予定の更新に失敗しました",
            }

    async def _delete_schedule(self, args: dict[str, Any]) -> dict[str, Any]:
        """予定削除"""
        response = await self.schedule_usecase.delete_schedule(
            args["user_id"],
            args["schedule_id"],
        )

        if response.success:
            return {
                "success": True,
                "message": "予定を削除しました",
            }
        else:
            return {
                "success": False,
                "error": response.error_message or "予定の削除に失敗しました",
            }

    async def _get_today_schedules(self, args: dict[str, Any]) -> dict[str, Any]:
        """今日の予定取得"""
        today = datetime.now().strftime("%Y-%m-%d")

        response = await self.schedule_usecase.get_schedules_by_date_range(
            args["user_id"],
            today,
            today,
        )

        if response.success:
            schedules_data = []
            for schedule in response.schedules:
                schedules_data.append(schedule.to_dict())

            # 時間順にソート
            schedules_data.sort(key=lambda x: x.get("start_datetime", ""))

            return {
                "success": True,
                "today_schedules": schedules_data,
                "count": len(schedules_data),
                "date": today,
                "message": f"今日は{len(schedules_data)}件の予定があります",
            }
        else:
            return {
                "success": False,
                "error": response.error_message or "今日の予定取得に失敗しました",
            }

    async def _suggest_schedule(self, args: dict[str, Any]) -> dict[str, Any]:
        """予定提案"""
        child_age_months = args["child_age_months"]
        interests = args.get("interests", [])
        available_days = args.get("available_days", [])

        suggestions = []

        # 月齢に応じた予定提案
        if child_age_months < 6:
            suggestions.extend([
                {
                    "title": "1ヶ月健診",
                    "description": "成長チェックと予防接種の相談",
                    "event_type": "medical",
                    "frequency": "monthly",
                    "importance": "high",
                },
                {
                    "title": "ベビーマッサージ教室",
                    "description": "親子のスキンシップとリラクゼーション",
                    "event_type": "other",
                    "frequency": "weekly",
                    "importance": "medium",
                },
            ])
        elif child_age_months < 12:
            suggestions.extend([
                {
                    "title": "離乳食教室",
                    "description": "月齢に応じた離乳食の作り方を学ぶ",
                    "event_type": "other",
                    "frequency": "monthly",
                    "importance": "high",
                },
                {
                    "title": "児童館でのふれあい遊び",
                    "description": "同年代のお友達との交流",
                    "event_type": "outing",
                    "frequency": "weekly",
                    "importance": "medium",
                },
            ])
        elif child_age_months < 24:
            suggestions.extend([
                {
                    "title": "1歳6ヶ月健診",
                    "description": "言葉の発達チェック",
                    "event_type": "medical",
                    "frequency": "once",
                    "importance": "high",
                },
                {
                    "title": "公園での外遊び",
                    "description": "運動能力の発達と自然との触れ合い",
                    "event_type": "outing",
                    "frequency": "daily",
                    "importance": "high",
                },
            ])
        else:
            suggestions.extend([
                {
                    "title": "幼児教室・習い事体験",
                    "description": "音楽、運動、アートなどの習い事",
                    "event_type": "school",
                    "frequency": "weekly",
                    "importance": "medium",
                },
                {
                    "title": "図書館での読み聞かせ",
                    "description": "言語発達と読書習慣の形成",
                    "event_type": "outing",
                    "frequency": "weekly",
                    "importance": "medium",
                },
            ])

        # 興味に応じた追加提案
        if "音楽" in interests:
            suggestions.append({
                "title": "リトミック教室",
                "description": "音楽に合わせた体動かし",
                "event_type": "school",
                "frequency": "weekly",
                "importance": "medium",
            })

        if "スポーツ" in interests:
            suggestions.append({
                "title": "ベビースイミング",
                "description": "水に慣れ親しむ運動",
                "event_type": "school",
                "frequency": "weekly",
                "importance": "medium",
            })

        return {
            "success": True,
            "child_age_months": child_age_months,
            "suggestions": suggestions,
            "available_days": available_days,
            "message": f"{len(suggestions)}件の予定を提案しました",
        }
