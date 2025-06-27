"""チャットサポートUseCase

コーディング規約準拠:
- Import文ファイル先頭配置
- 型アノテーション完備
- 統一戻り値形式
- DI注入ロガー
"""

import logging
from typing import Any


class ChatSupportUseCase:
    """チャットサポートのビジネスロジック
    
    フォローアップ質問生成、会話支援機能を提供
    """

    def __init__(self, logger: logging.Logger) -> None:
        """Args:
        logger: ロガー（DIコンテナから注入）

        """
        self.logger = logger

    def generate_followup_questions(self, original_message: str, specialist_response: str) -> dict[str, Any]:
        """回答内容に基づく動的フォローアップクエスチョン生成

        Args:
            original_message: 元の質問メッセージ
            specialist_response: 専門家の回答

        Returns:
            Dict[str, Any]: フォローアップ質問の生成結果

        """
        try:
            self.logger.info(f"フォローアップ質問生成開始: message='{original_message[:50]}...'")

            # ビジネスロジック: キーワードベースの質問生成
            questions = self._generate_questions_by_category(original_message, specialist_response)

            # ビジネスロジック: 質問のフォーマット
            formatted_questions = self._format_questions(questions)

            # ビジネスロジック: 最終メッセージ構築
            final_message = self._build_followup_message(formatted_questions)

            self.logger.info(f"フォローアップ質問生成完了: {len(questions)}件の質問を生成")

            return {
                "success": True,
                "formatted_message": final_message,
                "questions": questions,
                "question_count": len(questions),
            }

        except Exception as e:
            self.logger.error(f"フォローアップ質問生成エラー: {e}")
            return {
                "success": False,
                "error": str(e),
                "formatted_message": self._get_default_followup_message(),
            }

    def _generate_questions_by_category(self, original_message: str, specialist_response: str) -> list[str]:
        """カテゴリ別質問生成（ビジネスロジック）"""
        message_lower = original_message.lower()
        response_lower = specialist_response.lower()

        # 離乳食関連
        if any(word in message_lower or word in response_lower for word in ["離乳食", "食事", "栄養"]):
            return [
                "アレルギーが心配な時はどうすれば？",
                "食べない日が続く時の対処法は？",
                "手作りと市販品どちらがいい？",
            ]

        # 睡眠・夜泣き関連
        elif any(word in message_lower or word in response_lower for word in ["夜泣き", "睡眠", "寝かしつけ"]):
            return [
                "何時間くらいで改善しますか？",
                "昼寝の時間も関係ありますか？",
                "パパでも同じ方法で大丈夫？",
            ]

        # 発達関連
        elif any(word in message_lower or word in response_lower for word in ["発達", "成長", "言葉"]):
            return [
                "他の子と比べて遅れていませんか？",
                "家庭でできることはありますか？",
                "専門機関に相談するタイミングは？",
            ]

        # 健康関連
        elif any(word in message_lower or word in response_lower for word in ["体調", "健康", "熱", "病気"]):
            return [
                "病院に行く目安はありますか？",
                "家庭でできる対処法は？",
                "予防するにはどうすれば？",
            ]

        # 行動・しつけ関連
        elif any(word in message_lower or word in response_lower for word in ["しつけ", "行動", "イヤイヤ"]):
            return [
                "どのくらいの期間続きますか？",
                "効果的な声かけ方法は？",
                "やってはいけないことは？",
            ]

        # 遊び・学習関連
        elif any(word in message_lower or word in response_lower for word in ["遊び", "学習", "知育"]):
            return [
                "年齢に合った遊び方は？",
                "一人遊びができない時は？",
                "おもちゃの選び方のコツは？",
            ]

        # デフォルト（汎用的な質問）
        else:
            return [
                "他の親御さんはどう対処してますか？",
                "年齢によって方法は変わりますか？",
                "注意すべきサインはありますか？",
            ]

    def _format_questions(self, questions: list[str]) -> list[str]:
        """質問のフォーマット（ビジネスロジック）"""
        return [f"💭 {question}" for question in questions]

    def _build_followup_message(self, formatted_questions: list[str]) -> str:
        """フォローアップメッセージ構築（ビジネスロジック）"""
        return "**【続けて相談したい方へ】**\n" + "\n".join(formatted_questions)

    def _get_default_followup_message(self) -> str:
        """デフォルトフォローアップメッセージ（フォールバック）"""
        return "**【続けて相談したい方へ】**\n💭 具体的なやり方を教えて\n💭 うまくいかない時はどうする？\n💭 注意すべきポイントは？"
