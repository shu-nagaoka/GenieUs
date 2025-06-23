# Template for new Tool implementation
# 🚨 Claude Code: このテンプレートに従って実装してください
# 📋 必須参照: docs/guides/new-tool-development.md

# 1. Import文（必ずファイル先頭に配置）
import logging
from typing import Any, Dict, Optional
from google.adk.tools import FunctionTool
from src.application.usecases.{domain}_usecase import (
    {Domain}Request,
    {Domain}Response,
    {Domain}UseCase
)

# 2. ファクトリー関数（型アノテーション必須）
# 🚨 必須: ロガーDI注入パターン
def create_{domain}_function(
    usecase: {Domain}UseCase,
    logger: logging.Logger  # 🚨 必須: ロガーDI注入
) -> callable:
    """{Domain}ツール関数を作成するファクトリー（ロガーDI統合版）
    
    Args:
        usecase: 注入された{Domain}UseCaseインスタンス
        logger: ログ出力用（DIコンテナから注入）
        
    Returns:
        callable: ADK用ツール関数
    """
    
    def {domain}_function(
        message: str,
        user_id: str = "default_user",
        session_id: str = "default_session",
        additional_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """{Domain}を実行するADK用ツール関数
        
        Args:
            message: ユーザーからの入力
            user_id: ユーザーID
            session_id: セッションID
            additional_context: 追加のコンテキスト情報
            
        Returns:
            Dict[str, Any]: 処理結果（Agent向けに最適化された形式）
        """
        try:
            # リクエスト構築
            request = {Domain}Request(
                message=message,
                user_id=user_id,
                session_id=session_id,
                context=additional_context or {}
            )
            
            # ビジネスロジック実行
            response: {Domain}Response = usecase.execute(request)
            
            # Agent向けレスポンス変換（自然言語形式）
            if response.success:
                agent_response = f"""
                【{Domain}処理結果】
                
                {response.result}
                
                詳細:
                {response.details}
                
                推奨事項:
                {chr(10).join(f"• {rec}" for rec in response.recommendations)}
                """.strip()
                
                return {
                    "success": True,
                    "response": agent_response,
                    "metadata": {
                        "session_id": response.session_id,
                        "timestamp": response.timestamp.isoformat(),
                        "recommendations_count": len(response.recommendations)
                    }
                }
            else:
                return {
                    "success": False,
                    "response": response.error_message,
                    "metadata": {
                        "error": "usecase_execution_failed",
                        "session_id": response.session_id
                    }
                }
                
        except Exception as e:
            # フォールバック応答（段階的エラーハンドリング）
            logger.error(f"{Domain}ツールでエラー: {e}")  # ✅ 注入されたロガー使用
            
            return {
                "success": False,
                "response": "申し訳ございません。{Domain}処理で問題が発生しました。",
                "metadata": {
                    "error": "tool_execution_failed",
                    "error_details": str(e),
                    "session_id": session_id
                }
            }
    
    return {domain}_function

# 3. FunctionTool作成
# 🚨 必須: ロガーDI注入パターン
def create_{domain}_tool(
    usecase: {Domain}UseCase,
    logger: logging.Logger  # 🚨 必須: ロガーDI注入
) -> FunctionTool:
    """{Domain}FunctionTool作成（ロガーDI統合版）
    
    Args:
        usecase: 注入された{Domain}UseCaseインスタンス
        logger: ログ出力用（DIコンテナから注入）
        
    Returns:
        FunctionTool: ADKで使用可能な{Domain}ツール
    """
    # 関数を作成してからFunctionToolに渡す
    {domain}_func = create_{domain}_function(usecase, logger)
    
    return FunctionTool(func={domain}_func)

# 🚨 Claude Code チェックポイント:
# □ Import文がファイル先頭に配置されている
# □ 型アノテーションが完備されている
# □ エラーハンドリングが実装されている（段階的フォールバック）
# □ **ロガーDI注入が実装されている**（個別初期化禁止）
# □ ファクトリーパターンが適用されている
# □ Agent向けレスポンス変換が適切
# □ メタデータが適切に設定されている

# 📋 DIコンテナ統合例:
# class DIContainer(containers.DeclarativeContainer):
#     # ========== TOOLS LAYER - {Domain} ==========
#     {domain}_tool = providers.Factory(
#         create_{domain}_tool,
#         usecase={domain}_usecase,
#         logger=logger,  # 🚨 必須: ロガーDI注入
#     )