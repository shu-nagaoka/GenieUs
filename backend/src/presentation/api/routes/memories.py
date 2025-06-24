"""メモリー記録管理API"""

import json
from typing import Dict, Any, List, Optional
from uuid import uuid4
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Request, HTTPException, Depends
from pydantic import BaseModel

# データファイルのパス
DATA_DIR = Path(__file__).parent.parent.parent.parent.parent / "data"
MEMORY_RECORDS_FILE = DATA_DIR / "memories.json"

def load_memory_records() -> Dict[str, Any]:
    """メモリー記録データを読み込み"""
    if MEMORY_RECORDS_FILE.exists():
        with open(MEMORY_RECORDS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_memory_records(data: Dict[str, Any]) -> None:
    """メモリー記録データを保存"""
    DATA_DIR.mkdir(exist_ok=True)
    with open(MEMORY_RECORDS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

router = APIRouter(prefix="/memories", tags=["memories"])


class MemoryRecordCreateRequest(BaseModel):
    """メモリー記録作成リクエスト"""
    title: str
    description: str
    date: str
    type: str  # photo, video, album
    category: str  # milestone, daily, family, special
    media_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    location: Optional[str] = None
    tags: List[str] = []
    favorited: bool = False
    user_id: str = "frontend_user"


class MemoryRecordUpdateRequest(BaseModel):
    """メモリー記録更新リクエスト"""
    title: Optional[str] = None
    description: Optional[str] = None
    date: Optional[str] = None
    type: Optional[str] = None
    category: Optional[str] = None
    media_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    location: Optional[str] = None
    tags: Optional[List[str]] = None
    favorited: Optional[bool] = None
    user_id: str = "frontend_user"


@router.post("/create")
async def create_memory_record(
    request: MemoryRecordCreateRequest,
) -> Dict[str, Any]:
    """メモリー記録を作成"""
    try:
        memories = load_memory_records()
        memory_id = str(uuid4())
        request_data = request.model_dump()
        user_id = request_data.get("user_id", "frontend_user")
        
        memory_data = {
            "id": memory_id,
            "user_id": user_id,
            **request_data,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        memories[memory_id] = memory_data
        save_memory_records(memories)
        
        return {
            "success": True,
            "id": memory_id,
            "data": memory_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list")
async def get_memory_records(
    user_id: str = "frontend_user",
    type: Optional[str] = None,
    category: Optional[str] = None,
    favorited: Optional[bool] = None,
    tags: Optional[str] = None,
) -> Dict[str, Any]:
    """メモリー記録一覧を取得"""
    try:
        memories = load_memory_records()
        user_memories = [
            memory for memory in memories.values()
            if memory.get("user_id") == user_id
        ]
        
        # タイプでフィルタリング
        if type:
            user_memories = [
                memory for memory in user_memories
                if memory.get("type") == type
            ]
        
        # カテゴリでフィルタリング
        if category:
            user_memories = [
                memory for memory in user_memories
                if memory.get("category") == category
            ]
        
        # お気に入りでフィルタリング
        if favorited is not None:
            user_memories = [
                memory for memory in user_memories
                if memory.get("favorited") == favorited
            ]
        
        # タグでフィルタリング
        if tags:
            tag_list = [tag.strip() for tag in tags.split(",")]
            user_memories = [
                memory for memory in user_memories
                if any(tag in memory.get("tags", []) for tag in tag_list)
            ]
        
        # 日付でソート（新しい順）
        user_memories.sort(key=lambda x: x.get("date", ""), reverse=True)
        
        return {
            "success": True,
            "data": user_memories
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/detail/{memory_id}")
async def get_memory_record(
    memory_id: str,
    user_id: str = "frontend_user",
) -> Dict[str, Any]:
    """特定のメモリー記録を取得"""
    try:
        memories = load_memory_records()
        if memory_id not in memories:
            return {
                "success": False,
                "message": "メモリー記録が見つかりません"
            }
        
        memory = memories[memory_id]
        if memory.get("user_id") != user_id:
            raise HTTPException(status_code=403, detail="アクセス権限がありません")
        
        return {
            "success": True,
            "data": memory
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/update/{memory_id}")
async def update_memory_record(
    memory_id: str,
    request: MemoryRecordUpdateRequest,
) -> Dict[str, Any]:
    """メモリー記録を更新"""
    try:
        memories = load_memory_records()
        if memory_id not in memories:
            return {
                "success": False,
                "message": "メモリー記録が見つかりません"
            }
        
        request_data = request.model_dump(exclude_unset=True)
        user_id = request_data.get("user_id", "frontend_user")
        
        memory = memories[memory_id]
        if memory.get("user_id") != user_id:
            raise HTTPException(status_code=403, detail="アクセス権限がありません")
        
        # 更新データをマージ
        memory.update({
            **request_data,
            "updated_at": datetime.now().isoformat()
        })
        
        save_memory_records(memories)
        
        return {
            "success": True,
            "data": memory
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/delete/{memory_id}")
async def delete_memory_record(
    memory_id: str,
    user_id: str = "frontend_user",
) -> Dict[str, Any]:
    """メモリー記録を削除"""
    try:
        memories = load_memory_records()
        if memory_id not in memories:
            return {
                "success": False,
                "message": "メモリー記録が見つかりません"
            }
        
        memory = memories[memory_id]
        if memory.get("user_id") != user_id:
            raise HTTPException(status_code=403, detail="アクセス権限がありません")
        
        deleted_memory = memories.pop(memory_id)
        save_memory_records(memories)
        
        return {
            "success": True,
            "message": "メモリー記録を削除しました",
            "deleted_data": deleted_memory
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/favorite/{memory_id}")
async def toggle_memory_favorite(
    memory_id: str,
    favorited: bool,
    user_id: str = "frontend_user",
) -> Dict[str, Any]:
    """メモリーのお気に入り状態を切り替え"""
    try:
        memories = load_memory_records()
        if memory_id not in memories:
            return {
                "success": False,
                "message": "メモリー記録が見つかりません"
            }
        
        memory = memories[memory_id]
        if memory.get("user_id") != user_id:
            raise HTTPException(status_code=403, detail="アクセス権限がありません")
        
        memory["favorited"] = favorited
        memory["updated_at"] = datetime.now().isoformat()
        
        save_memory_records(memories)
        
        return {
            "success": True,
            "data": memory
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/favorites")
async def get_favorite_memories(
    user_id: str = "frontend_user",
) -> Dict[str, Any]:
    """お気に入りメモリーを取得"""
    try:
        memories = load_memory_records()
        favorite_memories = [
            memory for memory in memories.values()
            if memory.get("user_id") == user_id and memory.get("favorited") is True
        ]
        
        # 日付でソート（新しい順）
        favorite_memories.sort(key=lambda x: x.get("date", ""), reverse=True)
        
        return {
            "success": True,
            "data": favorite_memories
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/albums")
async def get_albums(
    user_id: str = "frontend_user",
) -> Dict[str, Any]:
    """アルバム一覧を取得"""
    try:
        memories = load_memory_records()
        albums = [
            memory for memory in memories.values()
            if memory.get("user_id") == user_id and memory.get("type") == "album"
        ]
        
        # 日付でソート（新しい順）
        albums.sort(key=lambda x: x.get("date", ""), reverse=True)
        
        return {
            "success": True,
            "data": albums
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tags")
async def get_memory_tags(
    user_id: str = "frontend_user",
) -> Dict[str, Any]:
    """使用中のタグ一覧を取得"""
    try:
        memories = load_memory_records()
        user_memories = [
            memory for memory in memories.values()
            if memory.get("user_id") == user_id
        ]
        
        # 全タグを収集
        all_tags = []
        for memory in user_memories:
            all_tags.extend(memory.get("tags", []))
        
        # 重複を削除してソート
        unique_tags = sorted(list(set(all_tags)))
        
        return {
            "success": True,
            "data": unique_tags
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))