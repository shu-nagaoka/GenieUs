"""Tool層共通レスポンスフォーマッター

全ツールが統一形式でAgentにレスポンスを返すための共通機能
"""

from typing import Any, Dict, List, Optional


class ToolResponse:
    """Tool層統一レスポンス形式"""

    def __init__(
        self,
        success: bool,
        message: str,
        data: Optional[Dict[str, Any]] = None,
        suggestions: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.success = success
        self.message = message
        self.data = data or {}
        self.suggestions = suggestions or []
        self.metadata = metadata or {}

    def to_agent_response(self) -> str:
        """Agent向け自然言語レスポンス生成"""
        response_parts = [self.message]

        # 提案・アドバイス追加
        if self.suggestions:
            response_parts.append(f"💡 アドバイス: {self.suggestions[0]}")

        return "\n\n".join(response_parts)

    def to_dict(self) -> Dict[str, Any]:
        """構造化データとして返す"""
        return {
            "success": self.success,
            "response": self.to_agent_response(),
            "data": self.data,
            "suggestions": self.suggestions,
            "metadata": self.metadata,
        }


class ChildcareResponseFormatter:
    """子育て相談特化レスポンスフォーマッター"""

    @staticmethod
    def image_analysis_success(
        detected_items: List[str],
        emotion: str,
        activity: str,
        confidence: float,
        suggestions: List[str],
        safety_concerns: List[str],
        child_id: str,
    ) -> ToolResponse:
        """画像分析成功レスポンス"""

        # メインメッセージ構築
        message_parts = []

        if detected_items:
            items_text = "、".join(detected_items[:3])
            message_parts.append(f"📸 画像から検出: {items_text}")

        if emotion != "unknown":
            message_parts.append(f"😊 お子さんの様子: {emotion}")

        if activity != "unknown":
            message_parts.append(f"🎯 活動内容: {activity}")

        # 信頼度表示
        confidence_text = "高い" if confidence > 0.7 else "中程度" if confidence > 0.4 else "低い"
        message_parts.append(f"📊 分析精度: {confidence_text}")

        # 安全性警告
        if safety_concerns:
            message_parts.append(f"⚠️ 注意点: {safety_concerns[0]}")

        main_message = "\n".join(message_parts)

        return ToolResponse(
            success=True,
            message=main_message,
            suggestions=suggestions,
            data={
                "detected_items": detected_items,
                "emotion": emotion,
                "activity": activity,
                "confidence": confidence,
                "safety_concerns": safety_concerns,
            },
            metadata={"tool_type": "image_analysis", "child_id": child_id},
        )

    @staticmethod
    def voice_analysis_success(
        emotion_detected: str,
        crying_type: str,
        needs_analysis: List[str],
        comfort_suggestions: List[str],
        child_id: str,
    ) -> ToolResponse:
        """音声分析成功レスポンス"""

        message_parts = []
        message_parts.append(f"🎵 音声分析結果:")

        if emotion_detected != "unknown":
            message_parts.append(f"😊 感情状態: {emotion_detected}")

        if crying_type != "unknown":
            message_parts.append(f"👶 泣き声タイプ: {crying_type}")

        if needs_analysis:
            needs_text = "、".join(needs_analysis[:2])
            message_parts.append(f"💭 推測される要求: {needs_text}")

        main_message = "\n".join(message_parts)

        return ToolResponse(
            success=True,
            message=main_message,
            suggestions=comfort_suggestions,
            data={"emotion_detected": emotion_detected, "crying_type": crying_type, "needs_analysis": needs_analysis},
            metadata={"tool_type": "voice_analysis", "child_id": child_id},
        )

    @staticmethod
    def record_management_success(operation: str, result_summary: str, data_count: int, child_id: str) -> ToolResponse:
        """記録管理成功レスポンス"""

        message_parts = []
        message_parts.append(f"📝 記録管理: {operation}")
        message_parts.append(f"📊 処理結果: {result_summary}")

        if data_count > 0:
            message_parts.append(f"📈 データ件数: {data_count}件")

        main_message = "\n".join(message_parts)

        return ToolResponse(
            success=True,
            message=main_message,
            suggestions=["記録を継続することで、より正確なパターン分析ができます"],
            data={"operation": operation, "data_count": data_count},
            metadata={"tool_type": "record_management", "child_id": child_id},
        )

    @staticmethod
    def file_management_success(operation: str, file_info: Dict[str, Any], child_id: str) -> ToolResponse:
        """ファイル管理成功レスポンス"""

        file_name = file_info.get("name", "不明")
        file_size = file_info.get("size", 0)

        message_parts = []
        message_parts.append(f"📁 ファイル操作: {operation}")
        message_parts.append(f"📄 ファイル: {file_name}")

        if file_size > 0:
            size_text = f"{file_size / 1024:.1f}KB" if file_size < 1024 * 1024 else f"{file_size / (1024 * 1024):.1f}MB"
            message_parts.append(f"📏 サイズ: {size_text}")

        main_message = "\n".join(message_parts)

        return ToolResponse(
            success=True,
            message=main_message,
            suggestions=["ファイルは安全に保存されました"],
            data=file_info,
            metadata={"tool_type": "file_management", "child_id": child_id},
        )

    @staticmethod
    def error_response(tool_type: str, error_message: str, child_id: str = "default_child") -> ToolResponse:
        """エラーレスポンス統一形式"""

        return ToolResponse(
            success=False,
            message=f"申し訳ございません。{tool_type}中に問題が発生しました。",
            suggestions=["しばらく時間をおいて再度お試しください"],
            metadata={"tool_type": tool_type, "child_id": child_id, "error": error_message},
        )
