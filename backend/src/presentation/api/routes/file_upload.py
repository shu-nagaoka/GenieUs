"""ファイルアップロード関連のAPIエンドポイント
"""

import os
import uuid
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/files", tags=["files"])

# アップロードディレクトリの設定
UPLOAD_DIR = Path(__file__).parent.parent.parent.parent / "data" / "uploads"
IMAGES_DIR = UPLOAD_DIR / "images"

# ディレクトリを作成（存在しない場合）
IMAGES_DIR.mkdir(parents=True, exist_ok=True)

# 許可されるファイル形式
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


class UploadResponse(BaseModel):
    success: bool
    file_url: str | None = None
    file_id: str | None = None
    message: str | None = None


def is_valid_image(filename: str) -> bool:
    """画像ファイルかどうかをチェック"""
    return Path(filename).suffix.lower() in ALLOWED_IMAGE_EXTENSIONS


@router.post("/upload/image", response_model=UploadResponse)
async def upload_image(file: UploadFile = File(...), user_id: str = Form(default="frontend_user")):
    """画像ファイルをアップロード
    """
    try:
        # ファイル形式のチェック
        if not is_valid_image(file.filename or ""):
            raise HTTPException(
                status_code=400, detail="サポートされていないファイル形式です。JPG、PNG、GIF、WebPのみ対応しています。",
            )

        # ファイルサイズのチェック
        file_content = await file.read()
        if len(file_content) > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="ファイルサイズが5MBを超えています。")

        # ユニークなファイル名を生成
        file_extension = Path(file.filename or "").suffix.lower()
        file_id = str(uuid.uuid4())
        new_filename = f"{file_id}{file_extension}"

        # ファイルを保存
        file_path = IMAGES_DIR / new_filename
        with open(file_path, "wb") as f:
            f.write(file_content)

        # ファイルURLを生成
        file_url = f"/api/v1/files/images/{new_filename}"

        return UploadResponse(
            success=True, file_url=file_url, file_id=file_id, message="画像が正常にアップロードされました",
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ファイルアップロード中にエラーが発生しました: {e!s}")


@router.get("/images/{filename}")
async def get_image(filename: str):
    """アップロードされた画像を取得
    """
    try:
        file_path = IMAGES_DIR / filename

        if not file_path.exists():
            raise HTTPException(status_code=404, detail="ファイルが見つかりません")

        # ファイル形式を確認
        if not is_valid_image(filename):
            raise HTTPException(status_code=400, detail="無効なファイル形式です")

        # ファイルのmedia typeを決定
        extension = Path(filename).suffix.lower()
        media_type_map = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".gif": "image/gif",
            ".webp": "image/webp",
        }

        media_type = media_type_map.get(extension, "application/octet-stream")

        return FileResponse(path=file_path, media_type=media_type, filename=filename)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ファイル取得中にエラーが発生しました: {e!s}")


@router.delete("/images/{filename}")
async def delete_image(filename: str, user_id: str = "frontend_user"):
    """アップロードされた画像を削除
    """
    try:
        file_path = IMAGES_DIR / filename

        if not file_path.exists():
            raise HTTPException(status_code=404, detail="ファイルが見つかりません")

        # ファイルを削除
        os.remove(file_path)

        return {"success": True, "message": "ファイルが削除されました"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ファイル削除中にエラーが発生しました: {e!s}")
