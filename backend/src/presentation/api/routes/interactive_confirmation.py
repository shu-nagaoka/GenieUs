"""Interactive Confirmation API - Human-in-the-Loop確認処理

ユーザーからの確認応答を受け取り、後続処理を実行するAPIエンドポイント
"""

from typing import Dict

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from src.application.usecases.interactive_confirmation_usecase import InteractiveConfirmationUseCase
from src.presentation.api.dependencies import get_interactive_confirmation_usecase

router = APIRouter()


class ConfirmationResponseRequest(BaseModel):
    """確認応答リクエスト"""

    confirmation_id: str
    user_response: str
    user_id: str
    session_id: str
    response_metadata: Dict = None


class ConfirmationResponseResponse(BaseModel):
    """確認応答レスポンス"""

    success: bool
    message: str
    followup_action: Dict
    confirmation_id: str
    timestamp: str


@router.post("/process-confirmation-response", response_model=ConfirmationResponseResponse)
async def process_confirmation_response(
    request: ConfirmationResponseRequest,
    interactive_confirmation_usecase: InteractiveConfirmationUseCase = Depends(get_interactive_confirmation_usecase),
) -> ConfirmationResponseResponse:
    """ユーザーの確認応答を処理する

    Args:
        request: 確認応答リクエスト
        interactive_confirmation_usecase: Interactive Confirmation UseCase

    Returns:
        ConfirmationResponseResponse: 処理結果とフォローアップアクション

    Raises:
        HTTPException: 処理エラー時
    """
    try:
        # UseCaseに処理を委譲
        result = await interactive_confirmation_usecase.process_confirmation_response(
            confirmation_id=request.confirmation_id,
            user_response=request.user_response,
            user_id=request.user_id,
            session_id=request.session_id,
            response_metadata=request.response_metadata,
        )

        if not result.get("success", False):
            raise HTTPException(status_code=400, detail=f"応答処理エラー: {result.get('error', '不明なエラー')}")

        return ConfirmationResponseResponse(
            success=True,
            message=result.get("message", "応答を正常に処理しました"),
            followup_action=result.get("followup_action", {}),
            confirmation_id=request.confirmation_id,
            timestamp=result.get("timestamp", ""),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"内部サーバーエラー: {str(e)}")
