"""努力記録管理Tool - EffortRecordUseCaseの薄いラッパー"""

import logging
from typing import Any

from google.adk.tools import FunctionTool


def create_effort_record_tool(
    logger: logging.Logger,
) -> FunctionTool:
    """努力記録管理ツール作成（簡易版）

    Args:
        logger: ロガー（DIコンテナから注入）

    Returns:
        FunctionTool: ADK用努力記録管理ツール

    """
    logger.info("努力記録管理ツール作成開始")

    def manage_effort_records(
        operation: str,
        user_id: str = "frontend_user",
        period_days: int = 7,
        effort_description: str = "",
        category: str = "",
        score: float = 0.0,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """努力記録のCRUD操作

        Args:
            operation: 操作タイプ（create, list, stats）
            user_id: ユーザーID
            period_days: 期間（日数）
            effort_description: 努力の説明
            category: カテゴリ（feeding, sleep, play, care）
            score: スコア（1-10）
            **kwargs: 追加パラメータ

        Returns:
            Dict[str, Any]: 操作結果

        """
        try:
            logger.info(f"努力記録ツール実行開始: operation={operation}, user_id={user_id}, period_days={period_days}")

            if operation == "create":
                # 努力記録作成
                if not effort_description:
                    return _create_error_response(operation, "努力の内容説明が必要です")

                # 簡易的な努力記録レスポンス
                return {
                    "success": True,
                    "response": f"✅ 「{effort_description}」を努力記録として保存しました！素晴らしい取り組みですね。",
                    "data": {
                        "description": effort_description,
                        "category": category,
                        "score": score,
                        "date": _get_today_date(),
                        "encouragement": _generate_encouragement(effort_description, category),
                    },
                    "metadata": {"operation": operation, "category": category},
                }

            elif operation == "list":
                # 努力記録一覧取得（モック）
                mock_efforts = _generate_mock_efforts(period_days)
                return {
                    "success": True,
                    "response": _format_efforts_list(mock_efforts, period_days),
                    "data": mock_efforts,
                    "metadata": {"operation": operation, "period_days": period_days, "count": len(mock_efforts)},
                }

            elif operation == "stats":
                # 努力統計取得（モック）
                stats = _generate_mock_stats(period_days)
                return {
                    "success": True,
                    "response": _format_effort_stats(stats, period_days),
                    "data": stats,
                    "metadata": {"operation": operation, "period_days": period_days},
                }

            elif operation == "encourage":
                # 励ましメッセージ生成
                return {
                    "success": True,
                    "response": _generate_encouragement_message(user_id),
                    "metadata": {"operation": operation},
                }

            else:
                return _create_error_response(operation, f"サポートされていない操作です: {operation}")

        except Exception as e:
            logger.error(f"努力記録ツール実行エラー: {e}")
            return _create_error_response(operation, f"処理中にエラーが発生しました: {e!s}")

    def _format_efforts_list(efforts: list[dict], period_days: int) -> str:
        """努力記録一覧のフォーマット"""
        if not efforts:
            return f"📋 過去{period_days}日間の努力記録はまだありません。今日から素晴らしい育児の記録を始めましょう！"

        response_parts = [f"💪 過去{period_days}日間の努力記録（{len(efforts)}件）:", ""]

        for i, effort in enumerate(efforts[:10]):  # 最新10件
            date = effort.get("date", "")
            description = effort.get("description", "")
            category_icon = _get_category_icon(effort.get("category", ""))
            response_parts.append(f"  {category_icon} {date}: {description}")

        if len(efforts) > 10:
            response_parts.append(f"  ...他{len(efforts) - 10}件の素晴らしい努力があります")

        response_parts.extend(["", "🌟 あなたの愛情と努力は、お子さんの成長にとってかけがえのない宝物です！"])

        return "\n".join(response_parts)

    def _format_effort_stats(stats: dict, period_days: int) -> str:
        """努力統計のフォーマット"""
        return f"""
📊 過去{period_days}日間の努力統計

💪 総努力回数: {stats["total_efforts"]}回
⭐ 平均スコア: {stats["average_score"]:.1f}/10
🔥 連続頑張り日数: {stats["streak_days"]}日

📈 カテゴリ別努力:
  🍼 食事・授乳: {stats["categories"]["feeding"]}%
  😴 睡眠サポート: {stats["categories"]["sleep"]}%
  🎮 遊び・学び: {stats["categories"]["play"]}%
  💖 ケア・愛情: {stats["categories"]["care"]}%

🎉 素晴らしい成果:
{chr(10).join(f"  ✨ {achievement}" for achievement in stats["achievements"])}

💡 あなたの愛情深い育児は、お子さんにとって最高の贈り物です。
   毎日の小さな努力が、大きな成長の礎となっています。
        """.strip()

    def _generate_mock_efforts(period_days: int) -> list[dict]:
        """モック努力記録生成"""
        efforts = []
        categories = ["feeding", "sleep", "play", "care"]
        descriptions = {
            "feeding": ["離乳食を丁寧に作りました", "好き嫌いに付き合いました", "栄養バランスを考えた食事"],
            "sleep": ["寝かしつけを頑張りました", "夜泣き対応しました", "安心できる環境作り"],
            "play": ["一緒に遊びました", "絵本を読みました", "公園で遊びました"],
            "care": ["おむつ替えを丁寧に", "お風呂でスキンシップ", "体調をしっかり観察"],
        }

        import random
        from datetime import datetime, timedelta

        for i in range(min(period_days * 2, 20)):  # 1日あたり2件程度
            date = (datetime.now() - timedelta(days=random.randint(0, period_days - 1))).strftime("%Y-%m-%d")
            category = random.choice(categories)
            description = random.choice(descriptions[category])

            efforts.append(
                {
                    "date": date,
                    "description": description,
                    "category": category,
                    "score": round(random.uniform(7.0, 10.0), 1),
                },
            )

        return sorted(efforts, key=lambda x: x["date"], reverse=True)

    def _generate_mock_stats(period_days: int) -> dict:
        """モック統計データ生成"""
        import random

        total_efforts = random.randint(period_days * 1, period_days * 3)

        return {
            "total_efforts": total_efforts,
            "average_score": round(random.uniform(7.5, 9.5), 1),
            "streak_days": min(random.randint(3, period_days), period_days),
            "categories": {
                "feeding": random.randint(20, 35),
                "sleep": random.randint(15, 30),
                "play": random.randint(20, 35),
                "care": random.randint(15, 30),
            },
            "achievements": [
                "毎日の愛情深いケア",
                "継続的な成長サポート",
                "忍耐強い寝かしつけ",
                "栄養バランスへの配慮",
            ],
        }

    def _generate_encouragement(effort_description: str, category: str) -> str:
        """努力に対する励ましメッセージ生成"""
        encouragements = {
            "feeding": "栄養への気遣いが素晴らしいです！お子さんの健やかな成長につながります。",
            "sleep": "安心できる睡眠環境づくり、ありがとうございます。お子さんもぐっすり眠れますね。",
            "play": "楽しい遊びの時間は、お子さんの心と体の発達にとても大切です。",
            "care": "愛情深いケア、本当に素晴らしいです。お子さんも安心していることでしょう。",
        }

        base_message = encouragements.get(category, "素晴らしい育児への取り組みです！")
        return f"{base_message} 毎日の積み重ねが、お子さんの幸せな成長を支えています。"

    def _generate_encouragement_message(user_id: str) -> str:
        """励ましメッセージ生成"""
        messages = [
            "🌟 あなたの愛情深い育児、本当に素晴らしいです！毎日お疲れさまです。",
            "💪 小さな努力の積み重ねが、お子さんの大きな成長につながっています。",
            "❤️ あなたの優しさと愛情が、お子さんにとって最高の贈り物です。",
            "🎉 今日も一日、お子さんと過ごせることに感謝ですね。素敵な家族時間です。",
            "✨ 完璧でなくても大丈夫。あなたなりの愛情表現が一番大切です。",
        ]
        import random

        return random.choice(messages)

    def _get_category_icon(category: str) -> str:
        """カテゴリアイコン取得"""
        icons = {"feeding": "🍼", "sleep": "😴", "play": "🎮", "care": "💖"}
        return icons.get(category, "✨")

    def _get_today_date() -> str:
        """今日の日付を取得"""
        from datetime import datetime

        return datetime.now().strftime("%Y-%m-%d")

    def _create_error_response(operation: str, error_message: str) -> dict[str, Any]:
        """エラーレスポンス作成"""
        return {
            "success": False,
            "response": f"❌ 努力記録{operation}操作でエラーが発生しました: {error_message}",
            "metadata": {"operation": operation, "error": error_message},
        }

    logger.info("努力記録管理ツール作成完了")
    return FunctionTool(func=manage_effort_records)
