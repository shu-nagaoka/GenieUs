"""認証API - Google OAuth + JWT統合"""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from src.application.usecases.user_management_usecase import UserManagementUseCase
from src.presentation.api.dependencies import (
    get_current_user_optional,
    get_current_user_required,
    get_user_management_usecase,
)

# ========== Request/Response Models ==========


class GoogleLoginRequest(BaseModel):
    """Google OAuth ログインリクエスト"""

    google_user_info: dict[str, Any] = Field(description="Google OAuth ユーザー情報")


class LoginResponse(BaseModel):
    """ログインレスポンス"""

    success: bool
    access_token: str | None = None
    token_type: str | None = None
    user: dict[str, Any] | None = None
    error: str | None = None
    detail: str | None = None


class UserProfileResponse(BaseModel):
    """ユーザープロフィールレスポンス"""

    success: bool
    user: dict[str, Any] | None = None
    error: str | None = None
    detail: str | None = None


class UpdateProfileRequest(BaseModel):
    """プロフィール更新リクエスト"""

    name: str | None = None
    picture_url: str | None = None
    locale: str | None = None


class TokenVerifyResponse(BaseModel):
    """トークン検証レスポンス"""

    success: bool
    user: dict[str, Any] | None = None
    token_payload: dict[str, Any] | None = None
    error: str | None = None
    detail: str | None = None


class RefreshTokenResponse(BaseModel):
    """トークンリフレッシュレスポンス"""

    success: bool
    access_token: str | None = None
    token_type: str | None = None
    error: str | None = None
    detail: str | None = None


# ========== API Router ==========

router = APIRouter()


# ========== 認証エンドポイント ==========


@router.post("/login/google", response_model=LoginResponse)
async def google_login(
    request: GoogleLoginRequest,
    user_management_usecase: UserManagementUseCase = Depends(get_user_management_usecase),
):
    """Google OAuthでログイン"""
    try:
        result = await user_management_usecase.login_with_google_oauth(
            request.google_user_info,
        )

        if result["success"]:
            return LoginResponse(
                success=True,
                access_token=result["access_token"],
                token_type=result["token_type"],
                user=result["user"],
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=result.get("error", "ログインに失敗しました"),
            )

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="内部サーバーエラー",
        )


@router.get("/profile", response_model=UserProfileResponse)
async def get_profile(
    current_user: dict[str, Any] = Depends(get_current_user_required),
    user_management_usecase: UserManagementUseCase = Depends(get_user_management_usecase),
):
    """ユーザープロフィール取得"""
    try:
        result = await user_management_usecase.get_user_profile(
            current_user["user_id"],
        )

        if result["success"]:
            return UserProfileResponse(
                success=True,
                user=result["user"],
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result.get("error", "ユーザーが見つかりません"),
            )

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="内部サーバーエラー",
        )


@router.put("/profile", response_model=UserProfileResponse)
async def update_profile(
    request: UpdateProfileRequest,
    current_user: dict[str, Any] = Depends(get_current_user_required),
    user_management_usecase: UserManagementUseCase = Depends(get_user_management_usecase),
):
    """ユーザープロフィール更新"""
    try:
        # リクエストデータを辞書に変換（Noneは除外）
        profile_data = {k: v for k, v in request.dict().items() if v is not None}

        result = await user_management_usecase.update_user_profile(
            current_user["user_id"],
            profile_data,
        )

        if result["success"]:
            return UserProfileResponse(
                success=True,
                user=result["user"],
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "プロフィール更新に失敗しました"),
            )

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="内部サーバーエラー",
        )


@router.delete("/account")
async def delete_account(
    current_user: dict[str, Any] = Depends(get_current_user_required),
    user_management_usecase: UserManagementUseCase = Depends(get_user_management_usecase),
):
    """ユーザーアカウント削除"""
    try:
        result = await user_management_usecase.delete_user_account(
            current_user["user_id"],
        )

        if result["success"]:
            return {"success": True, "message": result["message"]}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "アカウント削除に失敗しました"),
            )

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="内部サーバーエラー",
        )


@router.post("/verify", response_model=TokenVerifyResponse)
async def verify_token(
    current_user: dict[str, Any] | None = Depends(get_current_user_optional),
):
    """トークン検証"""
    try:
        if current_user:
            return TokenVerifyResponse(
                success=True,
                user=current_user,
                token_payload={"user_id": current_user["user_id"]},
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="無効なトークンです",
            )

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="内部サーバーエラー",
        )


@router.post("/refresh", response_model=RefreshTokenResponse)
async def refresh_token(
    current_user: dict[str, Any] = Depends(get_current_user_required),
    user_management_usecase: UserManagementUseCase = Depends(get_user_management_usecase),
):
    """トークンリフレッシュ"""
    try:
        result = await user_management_usecase.refresh_token(
            current_user["user_id"],
        )

        if result["success"]:
            return RefreshTokenResponse(
                success=True,
                access_token=result["access_token"],
                token_type=result["token_type"],
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=result.get("error", "トークンリフレッシュに失敗しました"),
            )

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="内部サーバーエラー",
        )


@router.get("/me")
async def get_current_user_info(
    current_user: dict[str, Any] = Depends(get_current_user_required),
):
    """現在のユーザー情報取得（簡易版）"""
    return {
        "user_id": current_user["user_id"],
        "email": current_user["email"],
        "name": current_user["name"],
        "auth_type": current_user["auth_type"],
    }
