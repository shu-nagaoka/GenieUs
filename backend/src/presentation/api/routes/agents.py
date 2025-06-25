"""
エージェント情報API
GenieUsの専門エージェント一覧とその詳細情報を提供
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter

router = APIRouter(prefix="/agents", tags=["agents"])


def get_agent_info() -> Dict[str, Any]:
    """エージェント情報を取得"""
    return {
        "coordinator": {
            "id": "coordinator",
            "name": "子育て相談のジーニー",
            "description": "基本的な子育ての悩みから複雑な相談まで、総合的にサポートします",
            "specialties": ["子育て相談", "育児アドバイス", "発達相談", "生活指導"],
            "icon": "🧙‍♂️",
            "color": "from-blue-500 to-cyan-500",
            "capabilities": ["24時間対応", "パーソナライズドアドバイス", "成長段階別サポート"],
            "status": "active",
        },
        "nutrition_specialist": {
            "id": "nutrition_specialist",
            "name": "栄養・食事のジーニー",
            "description": "離乳食から幼児食まで、栄養バランスを考えた食事をサポート",
            "specialties": ["離乳食指導", "幼児食レシピ", "アレルギー対応", "栄養相談"],
            "icon": "🍎",
            "color": "from-green-500 to-emerald-500",
            "capabilities": ["月齢別レシピ提案", "アレルギー対応レシピ", "栄養バランス分析"],
            "status": "active",
        },
        "sleep_specialist": {
            "id": "sleep_specialist",
            "name": "睡眠のジーニー",
            "description": "夜泣きや寝かしつけなど、睡眠に関する悩みを解決",
            "specialties": ["夜泣き対策", "寝かしつけ", "睡眠リズム", "ネントレ"],
            "icon": "🌙",
            "color": "from-purple-600 to-indigo-600",
            "capabilities": ["睡眠パターン分析", "個別ネントレプラン", "夜泣き原因特定"],
            "status": "active",
        },
        "development_specialist": {
            "id": "development_specialist",
            "name": "発達のジーニー",
            "description": "運動能力、言語発達、社会性など、お子さんの発達をサポート",
            "specialties": ["運動発達", "言語発達", "社会性発達", "マイルストーン"],
            "icon": "🌱",
            "color": "from-teal-500 to-green-500",
            "capabilities": ["発達段階チェック", "遊び提案", "刺激活動アドバイス"],
            "status": "active",
        },
        "health_specialist": {
            "id": "health_specialist",
            "name": "健康管理のジーニー",
            "description": "体調管理や病気の対応、予防接種スケジュールをサポート",
            "specialties": ["体調管理", "病気対応", "予防接種", "健診スケジュール"],
            "icon": "🏥",
            "color": "from-red-500 to-pink-500",
            "capabilities": ["症状チェック", "受診タイミング", "スケジュール管理"],
            "status": "active",
        },
        "play_specialist": {
            "id": "play_specialist",
            "name": "遊び・学びのジーニー",
            "description": "年齢に応じた遊びや学習活動を提案します",
            "specialties": ["知育遊び", "運動遊び", "創作活動", "学習サポート"],
            "icon": "🎨",
            "color": "from-orange-600 to-yellow-600",
            "capabilities": ["月齢別遊び提案", "室内・屋外活動", "DIY知育玩具"],
            "status": "active",
        },
        "discipline_specialist": {
            "id": "discipline_specialist",
            "name": "しつけのジーニー",
            "description": "イヤイヤ期やしつけの悩みを優しくサポートします",
            "specialties": ["イヤイヤ期対応", "しつけ方法", "行動修正", "感情コントロール"],
            "icon": "🎯",
            "color": "from-purple-500 to-pink-500",
            "capabilities": ["年齢別しつけ法", "ポジティブ育児", "問題行動対策"],
            "status": "active",
        },
        "emergency_specialist": {
            "id": "emergency_specialist",
            "name": "緊急時対応のジーニー",
            "description": "急な体調不良や事故時の応急処置をガイドします",
            "specialties": ["応急処置", "緊急時対応", "事故予防", "安全管理"],
            "icon": "🚨",
            "color": "from-red-700 to-red-900",
            "capabilities": ["緊急度判定", "ステップバイステップ指導", "予防策提案"],
            "status": "active",
        },
        "image_specialist": {
            "id": "image_specialist",
            "name": "画像解析のジーニー",
            "description": "写真から成長の記録や健康状態をチェックします",
            "specialties": ["画像解析", "成長記録", "健康チェック", "メモリー作成"],
            "icon": "📸",
            "color": "from-cyan-500 to-blue-500",
            "capabilities": ["AI画像認識", "成長分析", "写真整理"],
            "status": "active",
        },
        "voice_specialist": {
            "id": "voice_specialist",
            "name": "音声解析のジーニー",
            "description": "赤ちゃんの泣き声や言葉の発達を分析します",
            "specialties": ["泣き声分析", "言語発達", "音声認識", "コミュニケーション"],
            "icon": "🎤",
            "color": "from-pink-500 to-rose-500",
            "capabilities": ["泣き声パターン認識", "発話分析", "感情認識"],
            "status": "active",
        },
        "schedule_specialist": {
            "id": "schedule_specialist",
            "name": "スケジュール管理のジーニー",
            "description": "予防接種や健診、育児スケジュールを管理します",
            "specialties": ["スケジュール管理", "予防接種", "健診予定", "リマインダー"],
            "icon": "📅",
            "color": "from-violet-700 to-purple-700",
            "capabilities": ["自動スケジューリング", "リマインダー設定", "家族共有"],
            "status": "active",
        },
        "emotion_specialist": {
            "id": "emotion_specialist",
            "name": "感情サポートのジーニー",
            "description": "ママ・パパの感情面をサポートし、育児ストレスを軽減",
            "specialties": ["ストレス管理", "感情サポート", "メンタルヘルス", "リラクゼーション"],
            "icon": "💆‍♀️",
            "color": "from-rose-600 to-pink-600",
            "capabilities": ["ストレス診断", "リラックス法", "感情整理"],
            "status": "active",
        },
        "growth_specialist": {
            "id": "growth_specialist",
            "name": "成長記録のジーニー",
            "description": "お子さんの成長を記録し、発達の軌跡を可視化します",
            "specialties": ["成長記録", "データ分析", "発達グラフ", "マイルストーン管理"],
            "icon": "📊",
            "color": "from-emerald-500 to-teal-500",
            "capabilities": ["成長データ分析", "グラフ作成", "発達予測"],
            "status": "active",
        },
        "safety_specialist": {
            "id": "safety_specialist",
            "name": "安全管理のジーニー",
            "description": "家庭内の安全対策と事故防止をサポートします",
            "specialties": ["安全対策", "事故防止", "チャイルドプルーフ", "リスク管理"],
            "icon": "🛡️",
            "color": "from-amber-500 to-orange-500",
            "capabilities": ["安全チェックリスト", "リスク評価", "対策提案"],
            "status": "active",
        },
        "communication_specialist": {
            "id": "communication_specialist",
            "name": "コミュニケーションのジーニー",
            "description": "お子さんとの円滑なコミュニケーションをサポート",
            "specialties": ["親子コミュニケーション", "言葉かけ", "理解促進", "絆づくり"],
            "icon": "💬",
            "color": "from-blue-500 to-indigo-500",
            "capabilities": ["コミュニケーション術", "年齢別話し方", "絆深化法"],
            "status": "active",
        },
    }


@router.get("")
async def get_agents() -> Dict[str, Any]:
    """全エージェント一覧を取得"""
    try:
        agents_data = get_agent_info()
        agents_list = list(agents_data.values())

        return {"success": True, "data": agents_list, "message": "エージェント一覧を取得しました"}
    except Exception as e:
        return {"success": False, "message": f"エージェント一覧の取得に失敗しました: {str(e)}"}


@router.get("/{agent_id}")
async def get_agent(agent_id: str) -> Dict[str, Any]:
    """特定エージェントの詳細情報を取得"""
    try:
        agents_data = get_agent_info()

        if agent_id not in agents_data:
            return {"success": False, "message": "エージェントが見つかりません"}

        return {"success": True, "data": agents_data[agent_id], "message": "エージェント情報を取得しました"}
    except Exception as e:
        return {"success": False, "message": f"エージェント情報の取得に失敗しました: {str(e)}"}


@router.get("/stats/summary")
async def get_agents_stats() -> Dict[str, Any]:
    """エージェント統計情報を取得"""
    try:
        agents_data = get_agent_info()
        active_agents = [agent for agent in agents_data.values() if agent["status"] == "active"]

        return {
            "success": True,
            "data": {
                "total_agents": len(agents_data),
                "active_agents": len(active_agents),
                "agent_types": len(
                    set(agent["specialties"][0].split("・")[0] for agent in active_agents if agent["specialties"])
                ),
                "capabilities_count": sum(len(agent["capabilities"]) for agent in active_agents),
            },
            "message": "エージェント統計を取得しました",
        }
    except Exception as e:
        return {"success": False, "message": f"エージェント統計の取得に失敗しました: {str(e)}"}
