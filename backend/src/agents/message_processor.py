"""MessageProcessor - メッセージ処理とコンテキスト管理

メッセージの整形、コンテキスト管理、フォローアップ質問生成を担当
"""

import json
import logging
import re
from datetime import date, datetime

from google.adk.runners import Runner
from google.genai.types import Content, Part


class MessageProcessor:
    """メッセージ処理システム

    責務:
    - 会話履歴と家族情報を含むコンテキスト管理
    - メッセージ整形
    - フォローアップ質問生成
    - レスポンステキスト抽出
    """

    def __init__(self, logger: logging.Logger):
        """MessageProcessor初期化

        Args:
            logger: DIコンテナから注入されるロガー

        """
        self.logger = logger

    def create_message_with_context(
        self,
        message: str,
        conversation_history: list[dict] | None = None,
        family_info: dict | None = None,
        image_path: str = None,
        multimodal_context: dict = None,
    ) -> str:
        """会話履歴と家族情報、画像情報を含めたメッセージを作成"""
        context_parts = []

        # 家族情報セクション
        if family_info:
            self.logger.info(f"🏠 家族情報をプロンプトに含めます: {family_info}")
            family_text = self._format_family_info(family_info)
            context_parts.append(family_text)

        # 会話履歴セクション
        if conversation_history and len(conversation_history) > 0:
            history_text = self._format_conversation_history(conversation_history)
            context_parts.append(history_text)

        # 画像情報セクション（画像がある場合）
        if image_path:
            self.logger.info(f"🖼️ 画像添付を検出: {len(image_path) if image_path else 0}文字")
            # ファイルパスかBase64データかを判定
            if image_path.startswith("data:image/"):
                data_type = "Base64データ"
            elif "/" in image_path or "\\" in image_path:
                data_type = "ファイルパス"
            else:
                data_type = "不明な形式"
            
            image_text = f"【画像情報】\n画像タイプ: 子どもの写真が添付されています（{data_type}）\n"
            image_text += f"画像パス: {image_path}\n"
            image_text += f"分析指示: analyze_child_imageツールを使用して、上記の画像パス（{image_path}）を指定して画像を分析してください\n"
            
            if multimodal_context:
                image_description = multimodal_context.get('image_description', '')
                if image_description:
                    image_text += f"画像説明: {image_description}\n"
            context_parts.append(image_text)

        # 現在のメッセージ
        current_message = f"【現在のメッセージ】\n親御さん: {message}\n"
        context_parts.append(current_message)

        # 指示文
        if context_parts[:-1]:  # 家族情報や履歴がある場合
            instruction = self._create_contextual_instruction(family_info)
            context_parts.append(instruction)

        enhanced_message = "\n".join(context_parts)

        # ログ出力
        context_info = []
        if family_info:
            children_count = len(family_info.get("children", []))
            context_info.append(f"家族情報(子{children_count}人)")
        if conversation_history:
            context_info.append(f"履歴{len(conversation_history)}件")
        if image_path:
            context_info.append(f"画像データ({len(image_path)//1024}KB)")

        self.logger.info(
            f"📚 コンテキスト付きメッセージ作成: {', '.join(context_info) if context_info else '基本メッセージ'}",
        )

        return enhanced_message

    def _format_family_info(self, family_info: dict) -> str:
        """家族情報のフォーマット"""
        today = date.today()
        family_text = f"【家族情報】（本日: {today.strftime('%Y年%m月%d日')}）\n"

        # 子どもの情報
        children = family_info.get("children", [])
        if children:
            family_text += "お子さん:\n"
            for child in children:
                child_info = self._format_child_info(child, today)
                if child_info:
                    family_text += f"  - {', '.join(child_info)}\n"

        # 保護者情報
        if family_info.get("parent_name"):
            family_text += f"保護者: {family_info['parent_name']}\n"
        if family_info.get("family_structure"):
            family_text += f"家族構成: {family_info['family_structure']}\n"
        if family_info.get("living_area"):
            family_text += f"居住エリア: {family_info['living_area']}\n"
        if family_info.get("concerns"):
            family_text += f"主な心配事: {family_info['concerns']}\n"

        return family_text

    def _format_child_info(self, child: dict, today: date) -> list[str]:
        """子ども情報のフォーマット"""
        child_info = []

        if child.get("name"):
            child_info.append(f"お名前: {child['name']}")

        # 年齢を正確に計算
        if child.get("birth_date"):
            try:
                age_str = self._calculate_age(child["birth_date"], today)
                child_info.append(f"年齢: {age_str}")
                child_info.append(f"生年月日: {child['birth_date']}")
            except (ValueError, KeyError):
                # 日付解析に失敗した場合
                if child.get("age"):
                    child_info.append(f"年齢: {child['age']}")
                child_info.append(f"生年月日: {child['birth_date']}")
        elif child.get("age"):
            child_info.append(f"年齢: {child['age']}")

        if child.get("gender"):
            child_info.append(f"性別: {child['gender']}")
        if child.get("characteristics"):
            child_info.append(f"特徴: {child['characteristics']}")
        if child.get("allergies"):
            child_info.append(f"アレルギー: {child['allergies']}")
        if child.get("medical_notes"):
            child_info.append(f"健康メモ: {child['medical_notes']}")

        return child_info

    def _calculate_age(self, birth_date_str: str, today: date) -> str:
        """生年月日から年齢を計算"""
        import calendar

        birth_date = datetime.strptime(birth_date_str, "%Y-%m-%d").date()

        # 年齢計算
        years = today.year - birth_date.year
        months = today.month - birth_date.month
        days = today.day - birth_date.day

        # 誕生日がまだ来ていない場合の調整
        if months < 0 or (months == 0 and days < 0):
            years -= 1
            months += 12
        if days < 0:
            months -= 1
            prev_month = today.month - 1 if today.month > 1 else 12
            prev_year = today.year if today.month > 1 else today.year - 1
            days_in_prev_month = calendar.monthrange(prev_year, prev_month)[1]
            days += days_in_prev_month

        # 年齢表示の生成
        if years > 0:
            if months > 0:
                return f"{years}歳{months}ヶ月"
            else:
                return f"{years}歳"
        else:
            if months > 0:
                return f"{months}ヶ月"
            else:
                return f"{days}日"

    def _format_conversation_history(self, conversation_history: list[dict]) -> str:
        """会話履歴のフォーマット"""
        recent_history = conversation_history[-5:] if len(conversation_history) > 5 else conversation_history

        history_text = "【会話履歴】\n"
        for hist in recent_history:
            sender = hist.get("sender", "unknown")
            content = hist.get("content", "")
            if sender == "user":
                history_text += f"親御さん: {content}\n"
            elif sender == "assistant":
                history_text += f"アドバイザー: {content}\n"

        return history_text

    def _create_contextual_instruction(self, family_info: dict | None) -> str:
        """コンテキストに基づく指示文の作成"""
        greeting_instruction = ""
        if family_info and family_info.get("parent_name"):
            parent_name = family_info["parent_name"]
            greeting_instruction = (
                f"\n\n**重要**: 回答の冒頭で必ず「こんにちは！{parent_name}さん！」と親しみやすく挨拶してください。"
            )

        instruction = (
            f"\n上記の家族情報と会話履歴を踏まえて、お子さんの個性や状況に合わせた"
            f"個別的なアドバイスを提供してください。家族の状況を理解した上で、"
            f"親御さんの現在のメッセージに温かく回答してください。{greeting_instruction}"
        )

        return instruction

    def extract_response_text(self, response_content) -> str:
        """レスポンステキスト抽出"""
        if hasattr(response_content, "parts") and response_content.parts:
            response_text = ""
            for part in response_content.parts:
                if hasattr(part, "text") and part.text:
                    response_text += part.text
            return response_text
        elif isinstance(response_content, str):
            return response_content
        else:
            return str(response_content)

    async def generate_followup_questions(
        self,
        original_message: str,
        specialist_response: str,
        followup_runner: Runner | None = None,
        session_service=None,
    ) -> str:
        """専門家回答に基づくフォローアップクエスチョン生成"""
        try:
            self.logger.info("🔍 フォローアップクエスチョン生成開始")

            if not followup_runner:
                self.logger.warning("⚠️ フォローアップクエスチョン生成エージェントが利用できません")
                return self._generate_dynamic_fallback_questions(original_message, specialist_response)

            # フォローアップクエスチョン生成用のプロンプト作成
            followup_prompt = self._create_followup_prompt(original_message, specialist_response)

            # セッション作成
            session_id = "followup_gen"
            user_id = "system"

            if session_service:
                try:
                    await session_service.get_session(followup_runner.app_name, user_id, session_id)
                except Exception:
                    await session_service.create_session(
                        app_name=followup_runner.app_name,
                        user_id=user_id,
                        session_id=session_id,
                    )

            content = Content(role="user", parts=[Part(text=followup_prompt)])

            events = []
            async for event in followup_runner.run_async(
                user_id=user_id,
                session_id=session_id,
                new_message=content,
            ):
                events.append(event)

            if events and hasattr(events[-1], "content") and events[-1].content:
                followup_response = self.extract_response_text(events[-1].content)
                return self._format_followup_questions(followup_response)

            return ""

        except Exception as e:
            self.logger.error(f"フォローアップクエスチョン生成エラー: {e}")
            return ""

    def _create_followup_prompt(self, original_message: str, specialist_response: str) -> str:
        """フォローアップクエスチョン生成プロンプト作成"""
        return f"""
以下の専門家のアドバイスに基づいて、親御さんが続けて質問したくなるような具体的で実用的なフォローアップクエスチョンを3つ生成してください。

【元の相談内容】
{original_message}

【専門家からのアドバイス】
{specialist_response}

上記の専門家のアドバイス内容を分析し、「他の親御さんもよく聞かれる」ような自然で具体的な派生質問を3つ提案してください。

例：
- 専門家が離乳食について説明した場合 → 「アレルギーが心配な時はどうすれば？」「食べない日が続く時の対処法は？」「手作りと市販品どちらがいい？」
- 専門家が夜泣きについて説明した場合 → 「何時間くらいで改善しますか？」「昼寝の時間も関係ありますか？」「パパでも同じ方法で大丈夫？」

質問は以下の形式で回答してください：
{{
  "followup_questions": [
    "具体的で実用的な質問1",
    "具体的で実用的な質問2", 
    "具体的で実用的な質問3"
  ]
}}
"""

    def _format_followup_questions(self, followup_response: str) -> str:
        """フォローアップクエスチョンのフォーマット"""
        try:
            # JSON部分を抽出
            json_match = re.search(r"\{.*?\}", followup_response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                data = json.loads(json_str)
                questions = data.get("followup_questions", [])
            else:
                # JSON形式でない場合
                questions = self._extract_questions_from_text(followup_response)

            if not questions:
                return ""

            # 質問を整形
            formatted_questions = []
            for i, question in enumerate(questions[:3], 1):
                if question.strip():
                    formatted_questions.append(f"💭 {question}")

            if formatted_questions:
                return "\n".join(formatted_questions)

            return ""

        except Exception as e:
            self.logger.error(f"フォローアップクエスチョンフォーマットエラー: {e}")
            return "💭 具体的なやり方を教えて\n💭 うまくいかない時はどうする？\n💭 注意すべきポイントは？"

    def _extract_questions_from_text(self, text: str) -> list[str]:
        """テキストから質問を抽出"""
        lines = text.split("\n")
        questions = []

        for line in lines:
            line = line.strip()
            if line and ("？" in line or "?" in line) and len(line) < 50:
                # 不要な記号を除去
                clean_question = re.sub(r"^[-•\d\.\)\]\s]*", "", line)
                questions.append(clean_question)

        return questions[:3]

    def _generate_dynamic_fallback_questions(
        self,
        original_message: str,
        specialist_response: str,
    ) -> str:
        """回答内容に基づく動的フォールバック質問生成"""
        try:
            message_lower = original_message.lower()
            response_lower = specialist_response.lower()

            questions = []

            # キーワードベースの質問生成
            if any(word in message_lower or word in response_lower for word in ["離乳食", "食事", "栄養"]):
                questions = [
                    "アレルギーが心配な時はどうすれば？",
                    "食べない日が続く時の対処法は？",
                    "手作りと市販品どちらがいい？",
                ]
            elif any(word in message_lower or word in response_lower for word in ["夜泣き", "睡眠", "寝かしつけ"]):
                questions = [
                    "何時間くらいで改善しますか？",
                    "昼寝の時間も関係ありますか？",
                    "パパでも同じ方法で大丈夫？",
                ]
            elif any(word in message_lower or word in response_lower for word in ["発達", "成長", "言葉"]):
                questions = [
                    "他の子と比べて遅れていませんか？",
                    "家庭でできることはありますか？",
                    "専門機関に相談するタイミングは？",
                ]
            elif any(word in message_lower or word in response_lower for word in ["体調", "健康", "熱", "病気"]):
                questions = [
                    "病院に行く目安はありますか？",
                    "家庭でできる対処法は？",
                    "予防するにはどうすれば？",
                ]
            elif any(word in message_lower or word in response_lower for word in ["しつけ", "行動", "イヤイヤ"]):
                questions = [
                    "どのくらいの期間続きますか？",
                    "効果的な声かけ方法は？",
                    "やってはいけないことは？",
                ]
            else:
                questions = [
                    "他の親御さんはどう対処してますか？",
                    "年齢によって方法は変わりますか？",
                    "注意すべきサインはありますか？",
                ]

            formatted_questions = [f"💭 {q}" for q in questions]
            return "**【続けて相談したい方へ】**\n" + "\n".join(formatted_questions)

        except Exception as e:
            self.logger.error(f"動的フォールバック質問生成エラー: {e}")
            return (
                "**【続けて相談したい方へ】**\n"
                "💭 具体的なやり方を教えて\n"
                "💭 うまくいかない時はどうする？\n"
                "💭 注意すべきポイントは？"
            )

    def check_specialist_routing_keywords(self, response: str) -> bool:
        """専門家への紹介キーワードを検出"""
        response_lower = response.lower()

        routing_keywords = [
            "専門家",
            "専門医",
            "栄養士",
            "睡眠専門",
            "発達専門",
            "健康管理",
            "行動専門",
            "遊び専門",
            "安全専門",
            "心理専門",
            "仕事両立",
            "特別支援",
            "詳しく相談",
            "専門的なアドバイス",
            "より詳しく",
            "専門家に相談",
            "ジーニーが心を込めて",
            "ジーニーが",
            "お答えします",
            "回答します",
            "サポートします",
            "アドバイスします",
        ]

        return any(keyword in response_lower for keyword in routing_keywords)
