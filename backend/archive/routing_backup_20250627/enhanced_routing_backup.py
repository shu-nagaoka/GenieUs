"""強化されたルーティングシステム - LLMベース意図理解とキーワードマッチングのハイブリッド

キーワードマッチングの確実性とLLMの文脈理解力を組み合わせた
より精度の高いエージェントルーティングを実現
"""

import logging
import re

from src.agents.routing_strategy import RoutingStrategy


class EnhancedRoutingStrategy(RoutingStrategy):
    """LLMベース意図理解を統合したルーティングシステム"""

    def __init__(
        self,
        logger: logging.Logger,
        agent_keywords: dict[str, list[str]],
        force_routing_keywords: dict[str, list[str]],
        agent_priority: dict[str, float],
        keyword_weight: float = 0.4,
        llm_weight: float = 0.6,
    ) -> None:
        """Enhanced Routing Strategy初期化

        Args:
            logger: DIコンテナから注入されるロガー
            agent_keywords: エージェントごとのキーワードリスト
            force_routing_keywords: 強制ルーティング用キーワード
            agent_priority: エージェントの優先度
            keyword_weight: キーワードマッチングの重み
            llm_weight: LLM判定の重み

        """
        super().__init__(logger)
        self.agent_keywords = agent_keywords
        self.force_routing_keywords = force_routing_keywords
        self.agent_priority = agent_priority
        self.keyword_weight = keyword_weight
        self.llm_weight = llm_weight

    def determine_agent(
        self,
        message: str,
        conversation_history: list[dict] | None = None,
        family_info: dict | None = None,
    ) -> tuple[str, dict]:
        """Enhanced routing による エージェント決定

        キーワードマッチングとLLM分析を組み合わせた高度なルーティング
        """
        self.logger.info(f"🧠 Enhanced routing分析開始: '{message[:50]}...'")

        # ステップ1: 緊急度チェック（キーワードベース）
        emergency_result = self._check_emergency_routing(message)
        if emergency_result:
            self.logger.info("🚨 緊急ルーティング発動")
            return emergency_result

        # ステップ2: LLMベース意図理解
        llm_result = self._llm_intent_analysis(message, conversation_history, family_info)

        # ステップ3: キーワードマッチング
        keyword_result = self._keyword_analysis(message)

        # ステップ4: ハイブリッド決定
        final_agent, routing_info = self._hybrid_decision(llm_result, keyword_result, message)

        self.logger.info(f"🎯 Enhanced routing結果: {final_agent} (confidence: {routing_info['confidence']:.2f})")
        return final_agent, routing_info

    def get_strategy_name(self) -> str:
        """戦略名を返す"""
        return "EnhancedRouting"

    def _fallback_to_keyword_routing(self, message: str) -> tuple[str, dict]:
        """キーワードルーティングへのフォールバック"""
        # 簡易的なキーワードマッチング実装
        message_lower = message.lower()

        # 強制ルーティングチェック
        for agent_id, force_keywords in self.force_routing_keywords.items():
            if any(kw in message_lower for kw in force_keywords):
                return agent_id, {
                    "confidence": 1.0,
                    "reasoning": "緊急キーワードによる強制ルーティング",
                    "strategy": "enhanced_force",
                }

        # 専門エージェントマッチング
        for agent_id, keywords in self.agent_keywords.items():
            matched_keywords = [kw for kw in keywords if kw in message_lower]
            if matched_keywords:
                return agent_id, {
                    "confidence": 0.8,
                    "reasoning": f"キーワード {matched_keywords[:3]} にマッチ",
                    "strategy": "enhanced_keyword",
                }

        # デフォルト
        return "coordinator", {
            "confidence": 0.3,
            "reasoning": "デフォルトコーディネーター",
            "strategy": "enhanced_default",
        }

    def _check_emergency_routing(self, message: str) -> tuple[str, dict] | None:
        """緊急度チェック（高速キーワードベース）"""
        message_lower = message.lower()

        # 緊急キーワード
        emergency_keywords = [
            "緊急",
            "至急",
            "すぐに",
            "助けて",
            "危険",
            "事故",
            "怪我",
            "血",
            "息ができない",
            "意識がない",
            "高熱",
            "痙攣",
            "アレルギー",
            "救急車",
            "病院",
            "119",
        ]

        for keyword in emergency_keywords:
            if keyword in message_lower:
                return "health_specialist", {
                    "confidence": 1.0,
                    "reasoning": f"緊急キーワード「{keyword}」を検出",
                    "strategy": "enhanced_emergency",
                    "urgency": "high",
                }

        return None

    def _llm_intent_analysis(
        self,
        message: str,
        conversation_history: list[dict] | None = None,
        family_info: dict | None = None,
    ) -> dict:
        """LLMベース意図理解（改良されたパターンマッチング + 文脈理解）"""
        # 現在の実装では、ADKの技術的な制約により、
        # LLMベースの代替として高度なパターンマッチングとヒューリスティックスを使用

        self.logger.info("🧠 高度なパターンマッチング分析開始")

        message_lower = message.lower()
        context = self._build_context(conversation_history, family_info)

        # 文脈的分析パターン
        contextual_patterns = {
            "nutrition_specialist": {
                "keywords": [
                    "食事",
                    "離乳食",
                    "ミルク",
                    "栄養",
                    "食べない",
                    "アレルギー",
                    "授乳",
                    "献立",
                    "レシピ",
                    "偏食",
                    "食材",
                    "調理",
                    "メニュー",
                    "飲み込まない",
                    "飲み込まず",
                    "吐き出す",
                    "食べ物",
                ],
                "contexts": ["体重", "成長", "健康", "発達", "減って", "増えない"],
            },
            "sleep_specialist": {
                "keywords": ["睡眠", "寝ない", "夜泣き", "寝かしつけ", "昼寝", "寝付き", "夜中", "朝まで"],
                "contexts": ["疲れ", "時間", "習慣"],
            },
            "development_specialist": {
                "keywords": ["発達", "成長", "言葉", "歩く", "這う", "発語", "遅れ", "他の子", "比べて"],
                "contexts": ["年齢", "個人差", "心配", "指摘"],
            },
            "health_specialist": {
                "keywords": ["熱", "咳", "風邪", "病気", "薬", "病院", "予防接種", "症状", "体調", "受診"],
                "contexts": ["医師", "診察", "治療"],
            },
            "behavior_specialist": {
                "keywords": ["イヤイヤ", "癇癪", "しつけ", "叱る", "行動", "わがまま", "喧嘩", "反抗", "聞かない"],
                "contexts": ["対応", "方法", "困る"],
            },
            "work_life_specialist": {
                "keywords": [
                    "保育園",
                    "仕事復帰",
                    "職場復帰",
                    "両立",
                    "働く",
                    "職場",
                    "復職",
                    "保育",
                    "預ける",
                    "入園",
                    "保活",
                    "幼稚園",
                ],
                "contexts": ["選び", "準備", "不安"],
            },
            "mental_care_specialist": {
                "keywords": [
                    "疲れ",
                    "ストレス",
                    "不安",
                    "心配",
                    "うつ",
                    "落ち込",
                    "イライラ",
                    "気持ち",
                    "メンタル",
                    "辛い",
                ],
                "contexts": ["気分", "感情", "支援"],
            },
        }

        # 複合スコアリング
        agent_scores = {}

        for agent_id, patterns in contextual_patterns.items():
            keyword_matches = [kw for kw in patterns["keywords"] if kw in message_lower]
            context_matches = [ctx for ctx in patterns["contexts"] if ctx in message_lower]

            if keyword_matches or context_matches:
                # スコア計算（キーワード重視、文脈でブースト）
                keyword_score = len(keyword_matches) * 0.8
                context_score = len(context_matches) * 0.5

                # 特定パターンへの重み付け
                if agent_id == "nutrition_specialist" and any(
                    kw in ["飲み込まない", "飲み込まず", "吐き出す", "食べ物"] for kw in keyword_matches
                ):
                    keyword_score *= 1.5  # 栄養問題の重要性を高める

                total_score = keyword_score + context_score

                agent_scores[agent_id] = {
                    "score": total_score,
                    "keyword_matches": keyword_matches,
                    "context_matches": context_matches,
                    "confidence": min(0.9, total_score * 0.15),
                }

        # 最高スコアのエージェント選択
        if agent_scores:
            best_agent = max(agent_scores.items(), key=lambda x: x[1]["score"])
            agent_id, score_info = best_agent

            return {
                "recommended_agent": agent_id,
                "confidence": score_info["confidence"],
                "reasoning": f"高度分析: キーワード{score_info['keyword_matches'][:3]}, 文脈{score_info['context_matches'][:2]}",
                "urgency": self._analyze_urgency(message_lower),
                "emotion_tone": self._detect_emotion(message_lower),
            }

        # デフォルト
        return {
            "recommended_agent": "coordinator",
            "confidence": 0.4,
            "reasoning": "汎用的な相談として判定",
            "urgency": "low",
            "emotion_tone": self._detect_emotion(message_lower),
        }

    def _analyze_urgency(self, message_lower: str) -> str:
        """緊急度分析"""
        high_urgency = ["急", "すぐ", "至急", "危険", "救急", "緊急"]
        medium_urgency = ["心配", "困", "悩", "不安", "気になる"]

        if any(word in message_lower for word in high_urgency):
            return "high"
        elif any(word in message_lower for word in medium_urgency):
            return "medium"
        else:
            return "low"

    def _simple_llm_analysis(self, message: str) -> dict:
        """簡易的なルールベース LLM 分析"""
        message_lower = message.lower()

        # 高信頼度パターン
        patterns = {
            "nutrition_specialist": [
                "食事",
                "離乳食",
                "ミルク",
                "栄養",
                "食べない",
                "アレルギー",
                "授乳",
                "献立",
                "レシピ",
                "偏食",
                "食材",
                "調理",
                "メニュー",
            ],
            "sleep_specialist": ["睡眠", "寝ない", "夜泣き", "寝かしつけ", "昼寝", "寝付き"],
            "development_specialist": ["発達", "成長", "言葉", "歩く", "這う", "発語", "milestone"],
            "health_specialist": ["熱", "咳", "風邪", "病気", "薬", "病院", "予防接種", "症状"],
            "behavior_specialist": ["イヤイヤ", "癇癪", "しつけ", "叱る", "行動", "わがまま"],
            "play_learning_specialist": ["遊び", "おもちゃ", "学習", "教育", "絵本", "勉強"],
            "safety_specialist": ["安全", "事故", "怪我", "危険", "転落", "誤飲", "チャイルドロック"],
            "work_life_specialist": [
                "保育園",
                "仕事復帰",
                "職場復帰",
                "両立",
                "働く",
                "職場",
                "復職",
                "保育",
                "預ける",
                "入園",
                "保活",
            ],
            "mental_care_specialist": [
                "疲れ",
                "ストレス",
                "不安",
                "心配",
                "うつ",
                "落ち込",
                "イライラ",
                "気持ち",
                "メンタル",
            ],
            "search_specialist": ["検索", "調べて", "探して", "最新", "情報", "教えて", "知りたい"],
        }

        for agent, keywords in patterns.items():
            matched = [kw for kw in keywords if kw in message_lower]
            if matched:
                confidence = min(0.9, 0.6 + len(matched) * 0.1)
                return {
                    "recommended_agent": agent,
                    "confidence": confidence,
                    "reasoning": f"パターンマッチ: {matched[:3]}",
                    "urgency": "medium" if any(urgent in message_lower for urgent in ["急", "困", "心配"]) else "low",
                    "emotion_tone": self._detect_emotion(message_lower),
                }

        return {
            "recommended_agent": "coordinator",
            "confidence": 0.4,
            "reasoning": "汎用的な相談として判定",
            "urgency": "low",
            "emotion_tone": self._detect_emotion(message_lower),
        }

    def _detect_emotion(self, message_lower: str) -> str:
        """感情トーンの検出"""
        if any(word in message_lower for word in ["不安", "心配", "困", "悩"]):
            return "worried"
        elif any(word in message_lower for word in ["嬉しい", "良かった", "安心"]):
            return "happy"
        elif any(word in message_lower for word in ["わからない", "どう", "どうすれば"]):
            return "confused"
        else:
            return "neutral"

    def _keyword_analysis(self, message: str) -> dict:
        """キーワードマッチング分析"""
        message_lower = message.lower()

        # 最高マッチを検索
        best_agent = "coordinator"
        best_score = 0
        matched_keywords = []

        for agent_id, keywords in self.agent_keywords.items():
            current_matches = [kw for kw in keywords if kw in message_lower]
            score = len(current_matches) / len(keywords) if keywords else 0

            if score > best_score:
                best_score = score
                best_agent = agent_id
                matched_keywords = current_matches

        return {
            "recommended_agent": best_agent,
            "confidence": min(0.8, best_score * 2),
            "matched_keywords": matched_keywords,
            "reasoning": f"キーワードマッチ: {matched_keywords[:3]}" if matched_keywords else "キーワードマッチなし",
        }

    def _hybrid_decision(self, llm_result: dict, keyword_result: dict, message: str) -> tuple[str, dict]:
        """LLMとキーワード結果のハイブリッド決定"""
        # 重み付きスコア計算
        llm_agent = llm_result["recommended_agent"]
        keyword_agent = keyword_result["recommended_agent"]

        llm_score = llm_result["confidence"] * self.llm_weight
        keyword_score = keyword_result["confidence"] * self.keyword_weight

        # 一致している場合は信頼度アップ
        if llm_agent == keyword_agent:
            final_agent = llm_agent
            final_confidence = min(0.95, llm_score + keyword_score + 0.2)
            reasoning = f"LLMとキーワード分析が一致: {llm_agent}"
        else:
            # 異なる場合は高スコアを選択
            if llm_score > keyword_score:
                final_agent = llm_agent
                final_confidence = llm_score
                reasoning = f"LLM判定優先: {llm_agent} (LLM:{llm_score:.2f} > Keyword:{keyword_score:.2f})"
            else:
                final_agent = keyword_agent
                final_confidence = keyword_score
                reasoning = f"キーワード判定優先: {keyword_agent} (Keyword:{keyword_score:.2f} > LLM:{llm_score:.2f})"

        return final_agent, {
            "confidence": final_confidence,
            "reasoning": reasoning,
            "strategy": "enhanced_hybrid",
            "llm_result": llm_result,
            "keyword_result": keyword_result,
            "weights": {"llm": self.llm_weight, "keyword": self.keyword_weight},
        }

    def _build_context(self, conversation_history: list[dict] | None = None, family_info: dict | None = None) -> str:
        """コンテキスト情報の構築"""
        context_parts = []

        if family_info:
            context_parts.append(f"家族情報: {family_info}")

        if conversation_history:
            recent_messages = conversation_history[-3:] if len(conversation_history) > 3 else conversation_history
            context_parts.append(f"最近の会話: {recent_messages}")

        return "\n".join(context_parts) if context_parts else ""

    async def analyze_intent(self, message: str, llm_client) -> dict[str, any]:
        """LLMを使用してメッセージの意図を詳細分析

        Returns:
            {
                "intent_type": str,  # 相談、質問、緊急対応、情報検索など
                "urgency_level": int,  # 1-5 (5が最高緊急度)
                "emotion_tone": str,  # 不安、心配、喜び、困惑など
                "key_entities": list[str],  # 年齢、症状、行動など抽出されたエンティティ
                "suggested_agents": list[str],  # LLMが推奨するエージェント
                "confidence": float,  # 判定の確信度
                "reasoning": str  # 判定理由
            }

        """
        intent_prompt = f"""
        以下の子育て相談メッセージを分析し、JSONフォーマットで意図分析結果を返してください。

        メッセージ: "{message}"

        分析項目:
        1. intent_type: 以下から選択
           - "emergency" (緊急対応が必要)
           - "health_concern" (健康に関する心配)
           - "development_question" (発達に関する質問)
           - "daily_care" (日常ケアの相談)
           - "information_search" (情報検索・調査依頼)
           - "record_request" (記録・保存依頼)
           - "general_chat" (一般的な会話)
           
        2. urgency_level: 1-5の整数 (5が最高緊急度)
           - 5: 即座の対応が必要（熱、事故、緊急症状）
           - 4: 早急な対応が望ましい（健康不安、発達の心配）
           - 3: 通常の相談（日常的な悩み）
           - 2: 情報収集（一般的な質問）
           - 1: 雑談レベル
           
        3. emotion_tone: 感情的なトーン
           - "anxious" (不安・心配)
           - "urgent" (切迫・緊急)
           - "confused" (困惑・迷い)
           - "curious" (好奇心・興味)
           - "neutral" (中立・平常)
           
        4. key_entities: メッセージから抽出された重要な要素のリスト
           例: ["2歳", "夜泣き", "3日間", "38度", "離乳食"]
           
        5. suggested_agents: 最適と思われるエージェントID（最大3つ）
           利用可能なエージェント:
           - health_specialist (健康管理)
           - safety_specialist (安全・事故防止)
           - nutrition_specialist (栄養・食事)
           - sleep_specialist (睡眠)
           - development_specialist (発達支援)
           - behavior_specialist (行動・しつけ)
           - play_learning_specialist (遊び・学習)
           - mental_care_specialist (心理・メンタルケア)
           - search_specialist (検索・情報収集)
           - record_specialist (記録管理)
           - image_specialist (画像分析)
           - voice_specialist (音声分析)
           
        6. confidence: 0.0-1.0の小数（判定の確信度）
        
        7. reasoning: 判定理由の簡潔な説明（日本語）

        回答はJSON形式のみで、他の説明は不要です。
        """

        try:
            # LLM呼び出し（実際の実装ではADKのLLMクライアントを使用）
            response = await llm_client.generate(intent_prompt, temperature=0.1)

            # JSON解析
            import json

            result = json.loads(response)

            self.logger.info(f"🧠 LLM意図分析完了: {result}")
            return result

        except Exception as e:
            self.logger.error(f"LLM意図分析エラー: {e}")
            return self._get_fallback_intent()

    def _get_fallback_intent(self) -> dict[str, any]:
        """LLM分析失敗時のフォールバック"""
        return {
            "intent_type": "general_chat",
            "urgency_level": 3,
            "emotion_tone": "neutral",
            "key_entities": [],
            "suggested_agents": ["coordinator"],
            "confidence": 0.0,
            "reasoning": "LLM分析が失敗したため、デフォルト設定を使用",
        }

    def extract_contextual_keywords(self, message: str, intent_analysis: dict) -> list[str]:
        """意図分析結果を基に文脈的キーワードを拡張抽出

        例: "子どもが夜に食事を摂らない"
        → ["夜", "食事", "摂らない", "食べない", "夕食", "栄養不足"]
        """
        keywords = []
        message_lower = message.lower()

        # 基本的なキーワード抽出
        keywords.extend(intent_analysis.get("key_entities", []))

        # 文脈ベースの拡張
        contextual_expansions = {
            "食事を摂らない": ["食べない", "食欲不振", "拒食"],
            "夜に": ["夕食", "夜ごはん", "ディナー"],
            "朝に": ["朝食", "朝ごはん", "モーニング"],
            "お腹が": ["空腹", "満腹", "食欲"],
            "心配": ["不安", "気になる", "大丈夫か"],
            "どうしたら": ["対処法", "解決策", "方法"],
            "いつから": ["期間", "開始時期", "継続"],
            "検索": ["調べて", "探して", "教えて", "最新情報"],
            "近く": ["周辺", "近所", "地域", "アクセス"],
        }

        for pattern, expansions in contextual_expansions.items():
            if pattern in message_lower:
                keywords.extend(expansions)

        # 否定形の検出と変換
        negation_patterns = [
            (r"(.+)ない", r"\1"),  # 食べない → 食べ
            (r"(.+)くれない", r"\1"),  # 食べてくれない → 食べて
            (r"(.+)しない", r"\1"),  # 寝ない → 寝
        ]

        for pattern, replacement in negation_patterns:
            matches = re.findall(pattern, message_lower)
            for match in matches:
                base_word = re.sub(pattern, replacement, match + "ない")
                keywords.append(f"{base_word}_negation")  # 否定形であることをマーク

        # 重複除去
        return list(set(keywords))

    def calculate_hybrid_score(
        self,
        agent_id: str,
        keyword_score: float,
        llm_confidence: float,
        is_suggested_by_llm: bool,
        urgency_match: bool,
    ) -> float:
        """ハイブリッドスコアの計算

        キーワードマッチングとLLM判定の両方を考慮した総合スコア
        """
        # 基本スコア = キーワードスコア
        score = keyword_score

        # LLMが推奨した場合のボーナス
        if is_suggested_by_llm:
            score += 20 * llm_confidence  # 最大+20点

        # 緊急度マッチボーナス
        if urgency_match:
            score += 10

        # 特定パターンの優先処理
        priority_patterns = {
            "search_specialist": ["検索", "調べて", "探して", "最新", "情報"],
            "health_specialist": ["熱", "病院", "受診", "症状", "体調"],
            "safety_specialist": ["事故", "怪我", "危険", "緊急"],
        }

        # パターンマッチによる追加スコア
        if agent_id in priority_patterns:
            # この部分は実際のメッセージとのマッチングで実装
            pass

        return score

    def get_routing_explanation(
        self,
        selected_agent: str,
        keyword_matches: list[str],
        llm_analysis: dict,
        final_score: float,
    ) -> str:
        """ルーティング理由の説明文生成"""
        explanation_parts = []

        # キーワードマッチ
        if keyword_matches:
            explanation_parts.append(f"キーワード「{'、'.join(keyword_matches[:3])}」を検出")

        # LLM推奨
        if selected_agent in llm_analysis.get("suggested_agents", []):
            explanation_parts.append(f"AI分析により{llm_analysis.get('reasoning', '適切と判断')}")

        # 緊急度
        urgency = llm_analysis.get("urgency_level", 3)
        if urgency >= 4:
            explanation_parts.append("緊急性を考慮")

        # 最終スコア
        explanation_parts.append(f"総合スコア: {final_score:.1f}")

        return " | ".join(explanation_parts)


class RoutingFeedbackCollector:
    """ユーザーフィードバック収集とルーティング精度向上"""

    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.feedback_history = []

    def collect_feedback(
        self,
        message: str,
        selected_agent: str,
        user_satisfaction: int | None = None,  # 1-5
        was_correct_agent: bool | None = None,
        preferred_agent: str | None = None,
    ):
        """フィードバックの収集"""
        feedback = {
            "message": message,
            "selected_agent": selected_agent,
            "satisfaction": user_satisfaction,
            "correct_agent": was_correct_agent,
            "preferred_agent": preferred_agent,
            "timestamp": self._get_timestamp(),
        }

        self.feedback_history.append(feedback)

        # 一定数溜まったら分析・学習
        if len(self.feedback_history) >= 100:
            self._analyze_feedback_patterns()

    def _analyze_feedback_patterns(self):
        """フィードバックパターンの分析"""
        # 誤ルーティングパターンの検出
        misrouted_patterns = []

        for feedback in self.feedback_history:
            if feedback["correct_agent"] == False:
                misrouted_patterns.append(
                    {
                        "message_pattern": self._extract_pattern(feedback["message"]),
                        "wrong_agent": feedback["selected_agent"],
                        "correct_agent": feedback["preferred_agent"],
                    },
                )

        # パターンの集計と学習
        # 実装では、頻出する誤パターンを検出し、
        # キーワード辞書やスコアリング重みの調整に反映

        self.logger.info(f"📊 フィードバック分析完了: {len(misrouted_patterns)}件の改善点発見")

    def _extract_pattern(self, message: str) -> str:
        """メッセージからパターンを抽出"""
        # 簡易実装: 主要な名詞・動詞を抽出
        # 実際にはより高度な自然言語処理を使用
        return message[:50]  # 仮実装

    def _get_timestamp(self) -> str:
        """現在のタイムスタンプ取得"""
        from datetime import datetime

        return datetime.now().isoformat()
