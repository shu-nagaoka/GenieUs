"""成長記録管理API"""

import json
from typing import Dict, Any, List, Optional, Literal
from uuid import uuid4
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Request, HTTPException, Depends
from pydantic import BaseModel

# データファイルのパス
DATA_DIR = Path(__file__).parent.parent.parent.parent.parent / "data"
GROWTH_RECORDS_FILE = DATA_DIR / "growth_records.json"

def load_growth_records() -> Dict[str, Any]:
    """成長記録データを読み込み"""
    if GROWTH_RECORDS_FILE.exists():
        with open(GROWTH_RECORDS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_growth_records(data: Dict[str, Any]) -> None:
    """成長記録データを保存"""
    DATA_DIR.mkdir(exist_ok=True)
    with open(GROWTH_RECORDS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

router = APIRouter(prefix="/growth-records", tags=["growth_records"])


# 新しいカテゴリ型定義
GrowthType = Literal[
    "body_growth",      # からだの成長
    "language_growth",  # ことばの成長
    "skills",          # できること
    "social_skills",   # お友達との関わり
    "hobbies",         # 習い事・特技
    "life_skills",     # 生活スキル
    # 後方互換性のため従来タイプも保持
    "physical", "emotional", "cognitive", "milestone", "photo"
]

GrowthCategory = Literal[
    # からだの成長
    "height", "weight", "movement",
    # ことばの成長
    "speech", "first_words", "vocabulary",
    # できること
    "colors", "numbers", "puzzle", "drawing",
    # お友達との関わり
    "playing_together", "helping", "sharing", "kindness",
    # 習い事・特技
    "piano", "swimming", "dancing", "sports",
    # 生活スキル
    "toilet", "brushing", "dressing", "cleaning",
    # 従来カテゴリ（後方互換性）
    "smile", "expression", "achievement"
]

DetectedBy = Literal["genie", "parent"]

class GrowthRecordCreateRequest(BaseModel):
    """成長記録作成リクエスト"""
    child_id: Optional[str] = None  # 家族情報からの子どもID
    child_name: str
    date: str
    age_in_months: int
    type: GrowthType
    category: GrowthCategory
    title: str
    description: str
    value: Optional[str] = None
    unit: Optional[str] = None
    image_url: Optional[str] = None
    detected_by: DetectedBy = "parent"
    confidence: Optional[float] = None
    emotions: Optional[List[str]] = None
    development_stage: Optional[str] = None
    user_id: str = "frontend_user"


class GrowthRecordUpdateRequest(BaseModel):
    """成長記録更新リクエスト"""
    child_id: Optional[str] = None  # 家族情報からの子どもID
    child_name: Optional[str] = None
    date: Optional[str] = None
    age_in_months: Optional[int] = None
    type: Optional[GrowthType] = None
    category: Optional[GrowthCategory] = None
    title: Optional[str] = None
    description: Optional[str] = None
    value: Optional[str] = None
    unit: Optional[str] = None
    image_url: Optional[str] = None
    detected_by: Optional[DetectedBy] = None
    confidence: Optional[float] = None
    emotions: Optional[List[str]] = None
    development_stage: Optional[str] = None
    user_id: str = "frontend_user"


@router.post("/create")
async def create_growth_record(
    request: GrowthRecordCreateRequest,
) -> Dict[str, Any]:
    """成長記録を作成"""
    try:
        records = load_growth_records()
        record_id = str(uuid4())
        request_data = request.model_dump()
        user_id = request_data.get("user_id", "frontend_user")
        
        record_data = {
            "id": record_id,
            "user_id": user_id,
            **request_data,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        records[record_id] = record_data
        save_growth_records(records)
        
        return {
            "success": True,
            "id": record_id,
            "data": record_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list")
async def get_growth_records(
    user_id: str = "frontend_user",
    child_name: Optional[str] = None,
    type: Optional[str] = None,
    category: Optional[str] = None,
) -> Dict[str, Any]:
    """成長記録一覧を取得"""
    try:
        records = load_growth_records()
        user_records = [
            record for record in records.values()
            if record.get("user_id") == user_id
        ]
        
        # 子供の名前でフィルタリング
        if child_name:
            user_records = [
                record for record in user_records
                if record.get("child_name") == child_name
            ]
        
        # タイプでフィルタリング
        if type:
            user_records = [
                record for record in user_records
                if record.get("type") == type
            ]
        
        # カテゴリでフィルタリング
        if category:
            user_records = [
                record for record in user_records
                if record.get("category") == category
            ]
        
        # 日付でソート（新しい順）
        user_records.sort(key=lambda x: x.get("date", ""), reverse=True)
        
        return {
            "success": True,
            "data": user_records
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/detail/{record_id}")
async def get_growth_record(
    record_id: str,
    user_id: str = "frontend_user",
) -> Dict[str, Any]:
    """特定の成長記録を取得"""
    try:
        records = load_growth_records()
        if record_id not in records:
            return {
                "success": False,
                "message": "成長記録が見つかりません"
            }
        
        record = records[record_id]
        if record.get("user_id") != user_id:
            raise HTTPException(status_code=403, detail="アクセス権限がありません")
        
        return {
            "success": True,
            "data": record
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/update/{record_id}")
async def update_growth_record(
    record_id: str,
    request: GrowthRecordUpdateRequest,
) -> Dict[str, Any]:
    """成長記録を更新"""
    try:
        records = load_growth_records()
        if record_id not in records:
            return {
                "success": False,
                "message": "成長記録が見つかりません"
            }
        
        request_data = request.model_dump(exclude_unset=True)
        user_id = request_data.get("user_id", "frontend_user")
        
        record = records[record_id]
        if record.get("user_id") != user_id:
            raise HTTPException(status_code=403, detail="アクセス権限がありません")
        
        # 更新データをマージ
        record.update({
            **request_data,
            "updated_at": datetime.now().isoformat()
        })
        
        save_growth_records(records)
        
        return {
            "success": True,
            "data": record
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/delete/{record_id}")
async def delete_growth_record(
    record_id: str,
    user_id: str = "frontend_user",
) -> Dict[str, Any]:
    """成長記録を削除"""
    try:
        records = load_growth_records()
        if record_id not in records:
            return {
                "success": False,
                "message": "成長記録が見つかりません"
            }
        
        record = records[record_id]
        if record.get("user_id") != user_id:
            raise HTTPException(status_code=403, detail="アクセス権限がありません")
        
        deleted_record = records.pop(record_id)
        save_growth_records(records)
        
        return {
            "success": True,
            "message": "成長記録を削除しました",
            "deleted_data": deleted_record
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/milestones")
async def get_milestones(
    user_id: str = "frontend_user",
    child_name: Optional[str] = None,
) -> Dict[str, Any]:
    """マイルストーン記録を取得"""
    try:
        records = load_growth_records()
        user_records = [
            record for record in records.values()
            if record.get("user_id") == user_id and record.get("type") == "milestone"
        ]
        
        # 子供の名前でフィルタリング
        if child_name:
            user_records = [
                record for record in user_records
                if record.get("child_name") == child_name
            ]
        
        # 日付でソート（新しい順）
        user_records.sort(key=lambda x: x.get("date", ""), reverse=True)
        
        return {
            "success": True,
            "data": user_records
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/timeline")
async def get_growth_timeline(
    user_id: str = "frontend_user",
    child_name: Optional[str] = None,
    limit: int = 50,
) -> Dict[str, Any]:
    """成長タイムラインを取得"""
    try:
        records = load_growth_records()
        user_records = [
            record for record in records.values()
            if record.get("user_id") == user_id
        ]
        
        # 子供の名前でフィルタリング
        if child_name:
            user_records = [
                record for record in user_records
                if record.get("child_name") == child_name
            ]
        
        # 日付でソート（新しい順）
        user_records.sort(key=lambda x: x.get("date", ""), reverse=True)
        
        # 制限を適用
        if limit:
            user_records = user_records[:limit]
        
        return {
            "success": True,
            "data": user_records,
            "total_count": len(user_records)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/categories")
async def get_growth_categories() -> Dict[str, Any]:
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
                        {"value": "movement", "label": "運動・歩行", "unit": ""}
                    ]
                },
                "language_growth": {
                    "label": "ことばの成長",
                    "description": "言語・コミュニケーション発達の記録",
                    "color": "from-green-500 to-green-600",
                    "icon": "message-circle",
                    "categories": [
                        {"value": "speech", "label": "おしゃべり", "unit": ""},
                        {"value": "first_words", "label": "初めての言葉", "unit": ""},
                        {"value": "vocabulary", "label": "語彙", "unit": "語"}
                    ]
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
                        {"value": "drawing", "label": "お絵描き", "unit": ""}
                    ]
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
                        {"value": "kindness", "label": "やさしさ", "unit": ""}
                    ]
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
                        {"value": "sports", "label": "スポーツ", "unit": ""}
                    ]
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
                        {"value": "cleaning", "label": "お片付け", "unit": ""}
                    ]
                }
            }
        }
        
        return {
            "success": True,
            "data": categories
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/children")
async def get_children_for_growth_records(
    user_id: str = "frontend_user"
) -> Dict[str, Any]:
    """成長記録用の子ども一覧を取得（家族情報から）"""
    try:
        # 家族情報ファイルを読み込み
        family_file = DATA_DIR / f"{user_id}_family.json"
        
        if not family_file.exists():
            return {
                "success": True,
                "data": []
            }
        
        with open(family_file, "r", encoding="utf-8") as f:
            family_data = json.load(f)
        
        children = []
        for i, child in enumerate(family_data.get("children", [])):
            # 子どもIDを生成（実際のIDがない場合は、インデックスベースのIDを使用）
            child_id = f"{user_id}_child_{i}"
            
            # 生年月日から月齢を計算
            from datetime import datetime
            if child.get("birth_date"):
                birth_date = datetime.strptime(child["birth_date"], "%Y-%m-%d")
                current_date = datetime.now()
                age_in_months = (current_date.year - birth_date.year) * 12 + (current_date.month - birth_date.month)
                if current_date.day < birth_date.day:
                    age_in_months -= 1
            else:
                # 年齢文字列から推定
                age_str = child.get("age", "0")
                try:
                    age_years = int(age_str)
                    age_in_months = age_years * 12
                except:
                    age_in_months = 0
            
            children.append({
                "child_id": child_id,
                "name": child.get("name", ""),
                "age": child.get("age", ""),
                "age_in_months": age_in_months,
                "gender": child.get("gender", ""),
                "birth_date": child.get("birth_date", "")
            })
        
        return {
            "success": True,
            "data": children
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))