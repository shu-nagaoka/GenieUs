"""成長記録管理API - UseCase Pattern"""

from typing import Any, Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from src.application.usecases.growth_record_usecase import GrowthRecordUseCase
from src.presentation.api.dependencies import get_growth_record_usecase

router = APIRouter(prefix="/growth-records", tags=["growth_records"])


# 新しいカテゴリ型定義
GrowthType = Literal[
    "body_growth",  # からだの成長
    "language_growth",  # ことばの成長
    "skills",  # できること
    "social_skills",  # お友達との関わり
    "hobbies",  # 習い事・特技
    "life_skills",  # 生活スキル
    # 後方互換性のため従来タイプも保持
    "physical",
    "emotional",
    "cognitive",
    "milestone",
    "photo",
]

GrowthCategory = Literal[
    # からだの成長
    "height",
    "weight",
    "movement",
    # ことばの成長
    "speech",
    "first_words",
    "vocabulary",
    # できること
    "colors",
    "numbers",
    "puzzle",
    "drawing",
    # お友達との関わり
    "playing_together",
    "helping",
    "sharing",
    "kindness",
    # 習い事・特技
    "piano",
    "swimming",
    "dancing",
    "sports",
    # 生活スキル
    "toilet",
    "brushing",
    "dressing",
    "cleaning",
    # 従来カテゴリ（後方互換性）
    "smile",
    "expression",
    "achievement",
]

DetectedBy = Literal["genie", "parent"]


class GrowthRecordCreateRequest(BaseModel):
    """成長記録作成リクエスト"""

    child_id: str | None = None  # 家族情報からの子どもID
    child_name: str
    date: str
    age_in_months: int | None = None  # 生年月日から自動計算されるためオプショナル
    type: GrowthType
    category: GrowthCategory
    title: str
    description: str
    value: str | None = None
    unit: str | None = None
    image_url: str | None = None
    detected_by: DetectedBy = "parent"
    confidence: float | None = None
    emotions: list[str] | None = None
    development_stage: str | None = None
    user_id: str = "frontend_user"


class GrowthRecordUpdateRequest(BaseModel):
    """成長記録更新リクエスト"""

    child_id: str | None = None  # 家族情報からの子どもID
    child_name: str | None = None
    date: str | None = None
    age_in_months: int | None = None
    type: GrowthType | None = None
    category: GrowthCategory | None = None
    title: str | None = None
    description: str | None = None
    value: str | None = None
    unit: str | None = None
    image_url: str | None = None
    detected_by: DetectedBy | None = None
    confidence: float | None = None
    emotions: list[str] | None = None
    development_stage: str | None = None
    user_id: str = "frontend_user"


@router.post("/create")
async def create_growth_record(
    request: GrowthRecordCreateRequest,
    growth_record_usecase: GrowthRecordUseCase = Depends(get_growth_record_usecase),
) -> dict[str, Any]:
    """成長記録を作成"""
    try:
        request_data = request.model_dump()
        user_id = request_data.get("user_id", "frontend_user")

        result = await growth_record_usecase.create_growth_record(user_id=user_id, record_data=request_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list")
async def get_growth_records(
    user_id: str = "frontend_user",
    child_name: str | None = None,
    type: str | None = None,
    category: str | None = None,
    growth_record_usecase: GrowthRecordUseCase = Depends(get_growth_record_usecase),
) -> dict[str, Any]:
    """成長記録一覧を取得"""
    try:
        filters = {}
        if child_name:
            filters["child_name"] = child_name
        if type:
            filters["type"] = type
        if category:
            filters["category"] = category

        result = await growth_record_usecase.get_growth_records(user_id, filters)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/detail/{record_id}")
async def get_growth_record(
    record_id: str,
    user_id: str = "frontend_user",
    growth_record_usecase: GrowthRecordUseCase = Depends(get_growth_record_usecase),
) -> dict[str, Any]:
    """特定の成長記録を取得"""
    try:
        result = await growth_record_usecase.get_growth_record(user_id, record_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/update/{record_id}")
async def update_growth_record(
    record_id: str,
    request: GrowthRecordUpdateRequest,
    growth_record_usecase: GrowthRecordUseCase = Depends(get_growth_record_usecase),
) -> dict[str, Any]:
    """成長記録を更新"""
    try:
        request_data = request.model_dump(exclude_unset=True)
        user_id = request_data.get("user_id", "frontend_user")

        result = await growth_record_usecase.update_growth_record(
            user_id=user_id, record_id=record_id, update_data=request_data,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/delete/{record_id}")
async def delete_growth_record(
    record_id: str,
    user_id: str = "frontend_user",
    growth_record_usecase: GrowthRecordUseCase = Depends(get_growth_record_usecase),
) -> dict[str, Any]:
    """成長記録を削除"""
    try:
        result = await growth_record_usecase.delete_growth_record(user_id, record_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/milestones")
async def get_milestones(
    user_id: str = "frontend_user",
    child_name: str | None = None,
    growth_record_usecase: GrowthRecordUseCase = Depends(get_growth_record_usecase),
) -> dict[str, Any]:
    """マイルストーン記録を取得"""
    try:
        filters = {"type": "milestone"}
        if child_name:
            filters["child_name"] = child_name

        result = await growth_record_usecase.get_growth_records(user_id, filters)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/timeline")
async def get_growth_timeline(
    user_id: str = "frontend_user",
    child_name: str | None = None,
    limit: int = 50,
    growth_record_usecase: GrowthRecordUseCase = Depends(get_growth_record_usecase),
) -> dict[str, Any]:
    """成長タイムラインを取得"""
    try:
        filters = {}
        if child_name:
            filters["child_name"] = child_name

        result = await growth_record_usecase.get_growth_records(user_id, filters)

        # limitを適用
        if result.get("success") and limit:
            data = result.get("data", [])
            result["data"] = data[:limit]
            result["total_count"] = len(data)

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/categories")
async def get_growth_categories() -> dict[str, Any]:
    """成長記録のカテゴリ情報を取得"""
    try:
        categories = {
            "types": {
                "body_growth": {
                    "label": "からだの成長",
                    "description": "身長・体重・運動発達の記録",
                    "color": "from-blue-500 to-blue-600",
                    "icon": "ruler",
                    "categories": [
                        {"value": "height", "label": "身長", "unit": "cm"},
                        {"value": "weight", "label": "体重", "unit": "kg"},
                        {"value": "movement", "label": "運動・歩行", "unit": ""},
                    ],
                },
                "language_growth": {
                    "label": "ことばの成長",
                    "description": "言語・コミュニケーション発達の記録",
                    "color": "from-green-500 to-green-600",
                    "icon": "message-circle",
                    "categories": [
                        {"value": "speech", "label": "おしゃべり", "unit": ""},
                        {"value": "first_words", "label": "初めての言葉", "unit": ""},
                        {"value": "vocabulary", "label": "語彙", "unit": "語"},
                    ],
                },
                "skills": {
                    "label": "できること",
                    "description": "認知・学習スキルの記録",
                    "color": "from-purple-500 to-purple-600",
                    "icon": "star",
                    "categories": [
                        {"value": "colors", "label": "色がわかる", "unit": ""},
                        {"value": "numbers", "label": "数を数える", "unit": ""},
                        {"value": "puzzle", "label": "パズル", "unit": ""},
                        {"value": "drawing", "label": "お絵描き", "unit": ""},
                    ],
                },
                "social_skills": {
                    "label": "お友達との関わり",
                    "description": "社会性・情緒発達の記録",
                    "color": "from-pink-500 to-pink-600",
                    "icon": "heart",
                    "categories": [
                        {"value": "playing_together", "label": "一緒に遊ぶ", "unit": ""},
                        {"value": "helping", "label": "お手伝い", "unit": ""},
                        {"value": "sharing", "label": "分け合う", "unit": ""},
                        {"value": "kindness", "label": "やさしさ", "unit": ""},
                    ],
                },
                "hobbies": {
                    "label": "習い事・特技",
                    "description": "習い事・特技の習得記録",
                    "color": "from-amber-500 to-amber-600",
                    "icon": "award",
                    "categories": [
                        {"value": "piano", "label": "ピアノ", "unit": ""},
                        {"value": "swimming", "label": "水泳", "unit": ""},
                        {"value": "dancing", "label": "ダンス", "unit": ""},
                        {"value": "sports", "label": "スポーツ", "unit": ""},
                    ],
                },
                "life_skills": {
                    "label": "生活スキル",
                    "description": "日常生活スキルの記録",
                    "color": "from-teal-500 to-teal-600",
                    "icon": "target",
                    "categories": [
                        {"value": "toilet", "label": "トイレ", "unit": ""},
                        {"value": "brushing", "label": "歯磨き", "unit": ""},
                        {"value": "dressing", "label": "お着替え", "unit": ""},
                        {"value": "cleaning", "label": "お片付け", "unit": ""},
                    ],
                },
            },
        }

        return {"success": True, "data": categories}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/children")
async def get_children_for_growth_records(
    user_id: str = "frontend_user",
    growth_record_usecase: GrowthRecordUseCase = Depends(get_growth_record_usecase),
) -> dict[str, Any]:
    """成長記録用の子ども一覧を取得（家族情報から）"""
    try:
        result = await growth_record_usecase.get_children_for_growth_records(user_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
