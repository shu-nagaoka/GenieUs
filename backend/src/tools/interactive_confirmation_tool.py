"""InteractiveConfirmationTool - Human-in-the-Loop確認機能

エージェントがユーザーに対してインタラクティブに確認質問を行うためのツール
"""

import logging
from datetime import datetime
from typing import Dict


class InteractiveConfirmationTool:
    """Human-in-the-Loop確認ツール

    責務:
    - エージェントからユーザーへの確認質問生成
    - ユーザー応答の構造化
    - 確認結果のコンテキスト管理
    """

    def __init__(self, logger: logging.Logger):
        """InteractiveConfirmationTool初期化

        Args:
            logger: DIコンテナから注入されるロガー
        """
        self.logger = logger

    async def ask_user_confirmation(
        self,
        question: str,
        confirmation_type: str = "yes_no",
        timeout_seconds: int = 300,
        context_data: str = "",
    ):
        """ユーザーに確認質問を行う

        Args:
            question: ユーザーに表示する質問文
            confirmation_type: 確認タイプ（"yes_no", "multiple_choice", "custom"）
            timeout_seconds: 応答タイムアウト時間（秒）
            context_data: コンテキストデータ（JSON文字列形式）

        Returns:
            Dict: 確認質問情報とメタデータ
        """
        try:
            self.logger.info(f"🤝 ユーザー確認質問生成: {confirmation_type}")

            # デフォルトオプションを設定
            if confirmation_type == "yes_no":
                options = ["はい", "いいえ"]
            elif confirmation_type == "multiple_choice":
                options = ["選択肢1", "選択肢2", "選択肢3"]
            else:
                options = ["確認"]

            # コンテキストデータを設定（JSON文字列をパース）
            import json

            parsed_context_data = {}
            if context_data and context_data.strip():
                try:
                    parsed_context_data = json.loads(context_data)
                except json.JSONDecodeError:
                    self.logger.warning(f"Invalid JSON context_data: {context_data}")
                    parsed_context_data = {}

            # 確認質問データを構造化
            confirmation_data = {
                "confirmation_id": f"confirm_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "question": question,
                "options": options,
                "confirmation_type": confirmation_type,
                "context_data": parsed_context_data,
                "created_at": datetime.now().isoformat(),
                "timeout_seconds": timeout_seconds,
                "status": "pending",
            }

            # フロントエンド用の表示メッセージを生成
            display_message = self._generate_display_message(confirmation_data)

            result = {
                "success": True,
                "message": display_message,
                "confirmation_data": confirmation_data,
                "requires_user_response": True,
                "response_format": {
                    "type": "interactive_confirmation",
                    "confirmation_id": confirmation_data["confirmation_id"],
                    "options": options,
                },
            }

            self.logger.info(f"✅ 確認質問生成完了: {confirmation_data['confirmation_id']}")
            return result

        except Exception as e:
            self.logger.error(f"❌ 確認質問生成エラー: {e}")
            return {
                "success": False,
                "error": f"確認質問の生成中にエラーが発生しました: {str(e)}",
                "confirmation_data": None,
                "requires_user_response": False,
            }

    async def process_user_response(self, confirmation_id: str, user_response: str, response_metadata: str = ""):
        """ユーザー応答を処理する

        Args:
            confirmation_id: 確認質問ID
            user_response: ユーザーの応答
            response_metadata: 応答に関するメタデータ（JSON文字列形式）

        Returns:
            Dict: 処理結果とフォローアップ指示
        """
        try:
            self.logger.info(f"📥 ユーザー応答受信: {confirmation_id} -> {user_response}")

            # 応答を正規化
            normalized_response = self._normalize_user_response(user_response)

            # 応答メタデータを解析（JSON文字列をパース）
            import json

            parsed_metadata = {}
            if response_metadata and response_metadata.strip():
                try:
                    parsed_metadata = json.loads(response_metadata)
                except json.JSONDecodeError:
                    self.logger.warning(f"Invalid JSON response_metadata: {response_metadata}")
                    parsed_metadata = {}

            # 応答データを構造化
            response_data = {
                "confirmation_id": confirmation_id,
                "user_response": user_response,
                "normalized_response": normalized_response,
                "response_metadata": parsed_metadata,
                "processed_at": datetime.now().isoformat(),
                "is_positive": self._is_positive_response(normalized_response),
            }

            # フォローアップアクションを決定
            followup_action = self._determine_followup_action(response_data)

            result = {
                "success": True,
                "response_data": response_data,
                "followup_action": followup_action,
                "message": f"応答を受信しました: {user_response}",
            }

            self.logger.info(f"✅ ユーザー応答処理完了: {followup_action.get('action_type', 'none')}")
            return result

        except Exception as e:
            self.logger.error(f"❌ ユーザー応答処理エラー: {e}")
            return {
                "success": False,
                "error": f"応答処理中にエラーが発生しました: {str(e)}",
                "response_data": None,
                "followup_action": {"action_type": "error"},
            }

    def _generate_display_message(self, confirmation_data: Dict) -> str:
        """確認質問の表示メッセージを生成

        Args:
            confirmation_data: 確認質問データ

        Returns:
            str: フロントエンド表示用メッセージ
        """
        question = confirmation_data["question"]
        options = confirmation_data["options"]
        confirmation_type = confirmation_data["confirmation_type"]

        if confirmation_type == "yes_no":
            # はい/いいえ形式
            message = f"""
{question}

**選択してください：**
🔘 {options[0]}
🔘 {options[1]}

*下記のボタンから選択するか、チャットで「{options[0]}」または「{options[1]}」と入力してください。*
"""
        elif confirmation_type == "multiple_choice":
            # 複数選択形式
            options_text = "\n".join([f"🔘 {option}" for option in options])
            message = f"""
{question}

**選択してください：**
{options_text}

*下記のボタンから選択するか、チャットで選択肢を入力してください。*
"""
        else:
            # カスタム形式
            options_text = " / ".join(options)
            message = f"""
{question}

**選択肢：** {options_text}

*チャットでご回答ください。*
"""

        return message.strip()

    def _normalize_user_response(self, user_response: str) -> str:
        """ユーザー応答を正規化

        Args:
            user_response: 元の応答

        Returns:
            str: 正規化された応答
        """
        # 基本的な正規化処理
        normalized = user_response.strip().lower()

        # よくある応答パターンをマッピング
        positive_patterns = [
            "はい",
            "yes",
            "y",
            "ok",
            "おk",
            "いいです",
            "お願いします",
            "登録",
            "登録します",
            "保存",
            "保存します",
            "追加",
            "追加します",
        ]

        negative_patterns = [
            "いいえ",
            "no",
            "n",
            "やめます",
            "やめる",
            "不要",
            "結構です",
            "キャンセル",
            "取り消し",
            "やめておきます",
        ]

        for pattern in positive_patterns:
            if pattern in normalized:
                return "yes"

        for pattern in negative_patterns:
            if pattern in normalized:
                return "no"

        # パターンにマッチしない場合は元の応答を返す
        return normalized

    def _is_positive_response(self, normalized_response: str) -> bool:
        """応答が肯定的かどうかを判定

        Args:
            normalized_response: 正規化された応答

        Returns:
            bool: 肯定的な応答の場合True
        """
        return normalized_response == "yes"

    def _determine_followup_action(self, response_data: Dict):
        """フォローアップアクションを決定

        Args:
            response_data: 応答データ

        Returns:
            Dict: フォローアップアクション情報
        """
        is_positive = response_data["is_positive"]

        if is_positive:
            return {
                "action_type": "proceed",
                "message": "承知しました。処理を続行します。",
                "next_steps": ["execute_primary_action"],
            }
        else:
            return {
                "action_type": "cancel",
                "message": "承知しました。処理をキャンセルします。",
                "next_steps": ["show_alternative_options"],
            }

    async def create_confirmation_buttons(self, confirmation_data: Dict):
        """確認ボタンUIの生成

        Args:
            confirmation_data: 確認質問データ

        Returns:
            Dict: ボタンUI定義
        """
        try:
            confirmation_id = confirmation_data["confirmation_id"]
            options = confirmation_data["options"]

            buttons = []
            for i, option in enumerate(options):
                buttons.append(
                    {
                        "id": f"{confirmation_id}_option_{i}",
                        "text": option,
                        "value": option,
                        "style": "primary" if i == 0 else "secondary",
                    }
                )

            result = {
                "success": True,
                "button_group": {
                    "confirmation_id": confirmation_id,
                    "buttons": buttons,
                    "layout": "horizontal" if len(buttons) <= 3 else "vertical",
                },
            }

            self.logger.info(f"🔘 確認ボタン生成完了: {len(buttons)}個")
            return result

        except Exception as e:
            self.logger.error(f"❌ 確認ボタン生成エラー: {e}")
            return {"success": False, "error": f"ボタン生成中にエラーが発生しました: {str(e)}", "button_group": None}
