"""IntentBasedRoutingStrategy - 意図ベースルーティング戦略

ユーザーの明確な意図（検索、画像分析等）を最優先し、
UI状態に基づく強制ルーティングとキーワードマッチングを実装
"""

import logging

from src.agents.constants import AGENT_KEYWORDS, EXPLICIT_SEARCH_FLAGS
from src.agents.routing_strategy import RoutingStrategy


class IntentBasedRoutingStrategy(RoutingStrategy):
    """意図ベースルーティング戦略

    ユーザーの明確な意図（検索、画像分析等）を最優先し、
    UI状態に基づく強制ルーティングとキーワードマッチングを実装
    """

    def __init__(self, logger: logging.Logger):
        """初期化

        Args:
            logger: DIコンテナから注入されるロガー
        """
        self.logger = logger

    def determine_agent(
        self,
        message: str,
        conversation_history: list | None = None,
        family_info: dict | None = None,
        # 画像・マルチモーダル対応パラメータ追加
        has_image: bool = False,
        message_type: str = "text",
    ) -> tuple[str, dict]:
        """エージェント決定（キーワードマッチング + 文脈認識）

        Args:
            message: ユーザーメッセージ
            conversation_history: 会話履歴（確認文脈検出に使用）
            family_info: 家族情報（未使用）
            has_image: 画像添付フラグ
            message_type: メッセージタイプ

        Returns:
            Tuple[agent_id, routing_info]
        """
        message_lower = message.lower()

        # 🎯 **最優先**: 会話履歴から確認待ち状態を検出  
        self.logger.info(f"🔍 確認文脈チェック開始: conversation_history={bool(conversation_history)}, message='{message.strip()}'")
        if conversation_history and self._is_confirmation_context(conversation_history):
            self.logger.info(f"🔍 確認文脈検出成功、確認応答チェック: '{message.strip()}'")
            if message.strip() in ["はい", "yes", "Yes", "YES", "いいえ", "no", "No", "NO"]:
                is_positive = message.strip() in ["はい", "yes", "Yes", "YES"]
                if is_positive:
                    # 確認文脈のタイプを判定
                    context_type = self._get_confirmation_context_type(conversation_history)
                    self.logger.info(f"🔍 確認文脈タイプ判定結果: '{context_type}'")
                    
                    if context_type == "meal_record":
                        self.logger.info(f"🎯 食事記録確認応答検出（肯定）: '{message.strip()}' → 直接食事記録API実行")
                        return "meal_record_api", {
                            "confidence": 1.0,
                            "reasoning": "画像解析後の確認応答（肯定）- 直接食事記録API呼び出し",
                            "matched_keywords": [message.strip()],
                            "priority": "highest",
                            "confirmation_response": True,
                            "action": "create_meal_record_direct",
                            "api_call": True,
                        }
                    elif context_type == "schedule_record":
                        self.logger.info(f"🎯 スケジュール確認応答検出（肯定）: '{message.strip()}' → 直接スケジュール記録API実行")
                        return "schedule_record_api", {
                            "confidence": 1.0,
                            "reasoning": "スケジュール提案後の確認応答（肯定）- 直接スケジュール記録API呼び出し",
                            "matched_keywords": [message.strip()],
                            "priority": "highest",
                            "confirmation_response": True,
                            "action": "create_schedule_record_direct",
                            "api_call": True,
                        }
                    else:
                        self.logger.info(f"🎯 一般確認応答検出（肯定）: '{message.strip()}' → coordinatorで継続")
                        return "coordinator", {
                            "confidence": 1.0,
                            "reasoning": "一般確認応答（肯定）- 継続対話",
                            "matched_keywords": [message.strip()],
                            "priority": "highest",
                            "confirmation_response": True,
                            "action": "continue_conversation",
                        }
                else:
                    self.logger.info(f"🎯 確認応答検出（否定）: '{message.strip()}' → coordinatorで継続対話")
                    return "coordinator", {
                        "confidence": 1.0,
                        "reasoning": "確認応答（否定）- 継続対話",
                        "matched_keywords": [message.strip()],
                        "priority": "highest",
                        "confirmation_response": True,
                        "action": "continue_conversation",
                    }

        # 🖼️ **最優先**: 強制画像分析ルーティング指示検出
        if "FORCE_IMAGE_ANALYSIS_ROUTING" in message:
            self.logger.info(f"🎯 強制画像分析ルーティング指示検出 → image_specialist")
            return "image_specialist", {
                "confidence": 1.0,
                "reasoning": "フロントエンドからの強制画像分析ルーティング指示",
                "matched_keywords": ["FORCE_IMAGE_ANALYSIS_ROUTING"],
                "priority": "highest",
                "force_routing": True,
            }

        # 🖼️ **第2優先**: 画像添付検出
        if has_image or message_type == "image":
            self.logger.info(f"🎯 画像添付検出: has_image={has_image}, message_type={message_type} → image_specialist")
            return "image_specialist", {
                "confidence": 1.0,
                "reasoning": "画像添付検出による優先ルーティング",
                "matched_keywords": ["image_attachment"],
                "priority": "highest",
                "image_priority": True,
            }

        # 🔍 **第3優先**: 強制検索ルーティング指示検出
        if "FORCE_SEARCH_AGENT_ROUTING" in message:
            self.logger.info(f"🎯 強制検索ルーティング指示検出 → search_specialist")
            return "search_specialist", {
                "confidence": 1.0,
                "reasoning": "フロントエンドからの強制検索ルーティング指示",
                "matched_keywords": ["FORCE_SEARCH_AGENT_ROUTING"],
                "priority": "highest",
                "force_routing": True,
            }

        # 🔍 **第4優先**: 明示的検索フラグの検出
        for search_flag in EXPLICIT_SEARCH_FLAGS:
            if search_flag.lower() in message_lower or search_flag in message:
                self.logger.info(f"🎯 明示的検索フラグ検出: '{search_flag}' → search_specialist")
                return "search_specialist", {
                    "confidence": 1.0,
                    "reasoning": f"明示的検索要求フラグ検出: {search_flag}",
                    "matched_keywords": [search_flag],
                    "priority": "highest",
                    "explicit_search": True,
                }

        # 各エージェントのキーワードマッチング
        # 🔍 改善: すべてのエージェントをチェックし、最もマッチ数が多いものを選択
        best_agent_id = None
        best_match_count = 0
        best_routing_info = None
        
        for agent_id, keywords in AGENT_KEYWORDS.items():
            match_count = sum(1 for keyword in keywords if keyword in message_lower)
            if match_count > best_match_count:
                best_match_count = match_count
                best_agent_id = agent_id
                confidence = min(match_count / len(keywords), 1.0)
                best_routing_info = {
                    "confidence": confidence,
                    "reasoning": f"キーワードマッチ: {match_count}個",
                    "matched_keywords": [kw for kw in keywords if kw in message_lower],
                }
                self.logger.info(f"🎯 新しい最適エージェント: {agent_id} (マッチ数: {match_count})")

        if best_agent_id:
            self.logger.info(f"✅ 最終選択エージェント: {best_agent_id} (マッチ数: {best_match_count})")
            return best_agent_id, best_routing_info

        # デフォルトはコーディネーター
        return "coordinator", {"confidence": 0.5, "reasoning": "デフォルトルーティング", "matched_keywords": []}

    def _is_confirmation_context(self, conversation_history: list) -> bool:
        """会話履歴から確認待ち状態を検出
        
        Args:
            conversation_history: 会話履歴リスト
            
        Returns:
            bool: 確認待ち状態の場合True
        """
        self.logger.info(f"🔍 _is_confirmation_context開始: history_length={len(conversation_history) if conversation_history else 0}")
            
        if not conversation_history or len(conversation_history) == 0:
            self.logger.info("🔍 会話履歴なし、確認文脈なし")
            return False
            
        # 直前のメッセージ（エージェントからの応答）を確認
        last_message = conversation_history[-1] if conversation_history else None
        if not last_message:
            self.logger.info("🔍 直前メッセージなし、確認文脈なし")
            return False
            
        self.logger.info(f"🔍 直前メッセージチェック: role={last_message.get('role')}, content_length={len(last_message.get('content', ''))}")
            
        # エージェントからのメッセージで確認文脈を含むかチェック
        role = last_message.get("role")
        self.logger.info(f"🔍 メッセージrole詳細: '{role}' (type: {type(role)})")
        
        # より包括的なroleチェック（エージェントからの応答と判定）
        agent_roles = ["genie", "assistant", "agent", "bot", None, ""]
        if role in agent_roles:
            content = last_message.get("content", "")
            self.logger.info(f"🔍 確認文脈チェック対象content: '{content[:200]}{'...' if len(content) > 200 else ''}'")
            
            # 確認文脈の特徴的なキーワードを検出（食事・スケジュール両方）
            confirmation_indicators = [
                # 食事・画像解析関連
                "detected_items",  # 検出されたアイテム
                "画像を分析",
                "写真を見て",
                "分析結果",
                "食事の記録を作成しますか",
                "記録を作成",
                "登録いたしますか",
                "記録しますか",
                "食事記録",
                "栄養・食事のジーニー",  # 栄養専門家からの提案
                "食事管理",
                "お写真の分析ができました",  # 実際のレスポンスパターン
                "画像分析専門家",
                "分析してほしい画像",
                "お写真からは",
                "この献立は",
                "毎日の食事管理の記録として",
                "お食事中のお写真",  # 実際のレスポンス
                "拝見しましたところ",
                "お食事は",
                "豆腐やトマト",
                "美味しそうで",
                "食べていたのでしょうね",
                # エラー・確認時のキーワード追加
                "お食事の記録のご提案",
                "システムの方で少し問題が発生",
                "自動で記録の確認",
                "食事の記録を、引き続きお手伝い",
                "「はい」か「いいえ」",
                "記録しておきませんか",
                "食事管理システムに記録",
                "今後の栄養バランスの参考",
                "日佳梨ちゃんの大切な食事の記録",
                # スケジュール・予定関連の確認文脈
                "予定を登録",
                "スケジュールに記録",
                "カレンダーに記録",
                "予約の確認",
                "予定の確認",
                "スケジュール管理",
                "リマインダー設定",
                "予定を追加",
                "登録しておきませんか",
                "記録しておきませんか",
                "予約を記録",
                "診察の予定",
                "検診の予約",
                "健診の予定",
                "予防接種の予定",
                "病院の予約",
                "クリニックの予約",
                "通院予定",
                "医院の予約",
                "小児科の予約",
                "カレンダーに記録しておきませんか",
                "スケジュールに記録しておきませんか",
                "予定を管理",
                "忘れないように記録",
                "準備を忘れずに済みます",
                "当日の持ち物チェック",
                "便利ですよ",
                "いかがでしょうか"
            ]
            
            # 確認文脈（食事・スケジュール）の提案が含まれているかチェック
            for indicator in confirmation_indicators:
                if indicator in content:
                    self.logger.info(f"🔍 確認文脈検出成功: '{indicator}' が含まれる前回応答")
                    return True
            
            self.logger.info(f"🔍 確認文脈検出失敗: 確認キーワードなし、content_preview='{content[:100]}...'")
                    
        return False

    def _get_confirmation_context_type(self, conversation_history: list) -> str:
        """確認文脈のタイプを判定（food vs schedule vs general）
        
        Args:
            conversation_history: 会話履歴
            
        Returns:
            str: "meal_record", "schedule_record", または "general"
        """
        self.logger.info(f"🔍 _get_confirmation_context_type開始: history_length={len(conversation_history) if conversation_history else 0}")
        
        if not conversation_history:
            self.logger.info("🔍 会話履歴なし、generalを返す")
            return "general"
        
        # 🚨 **重要**: 直前のメッセージ（1件のみ）をチェック - 異なる文脈の混在を防ぐ
        last_message = conversation_history[-1] if conversation_history else None
        
        if last_message:
            role = last_message.get("role")
            content = last_message.get("content", "")
            
            # エージェントからのメッセージをチェック
            if role == "genie" or role is None or role == "":
                # 食事記録関連の確認文脈
                meal_indicators = [
                    "食事記録",
                    "食事管理",
                    "栄養記録",
                    "お食事の記録",
                    "食事管理システムに記録",
                    "栄養バランスの参考",
                    "画像分析",
                    "お写真",
                    "分析結果",
                    "献立",
                    "食べ物",
                    "離乳食",
                    "記録しておきませんか",
                ]
                
                # スケジュール記録関連の確認文脈
                schedule_indicators = [
                    "予定",
                    "スケジュール",
                    "診察",
                    "検診",
                    "健診",
                    "予約",
                    "カレンダー",
                    "予定表",
                    "予定を登録",
                    "スケジュールに記録",
                    "予定を追加",
                    "リマインダー",
                    "アラーム",
                    "忘れないように",
                    "記録しておく",
                    "次回の予約",
                    "来週の診察",
                    "来月の検診",
                    "病院予約",
                    "通院予定",
                    "ワクチン接種",
                    "予防接種の予定",
                    "キッズクリニック",
                    "クリニック",
                    "小児科",
                    "病院",
                    "医院",
                    "カレンダーに記録しておきませんか",
                    "記録しておきませんか",
                    "登録しておきませんか",
                    "準備を忘れずに済みます",
                    "当日の持ち物チェック",
                    "便利ですよ",
                    "いかがでしょうか"
                ]
                
                # キーワード数を比較して、より多くマッチした方を優先
                schedule_count = sum(1 for indicator in schedule_indicators if indicator in content)
                meal_count = sum(1 for indicator in meal_indicators if indicator in content)
                
                # デバッグ: マッチしたキーワードを表示
                matched_schedule = [indicator for indicator in schedule_indicators if indicator in content]
                matched_meal = [indicator for indicator in meal_indicators if indicator in content]
                
                self.logger.info(f"🔍 確認文脈キーワード一致数: 食事={meal_count}個, スケジュール={schedule_count}個")
                self.logger.info(f"🔍 マッチしたスケジュールキーワード: {matched_schedule}")
                self.logger.info(f"🔍 マッチした食事キーワード: {matched_meal}")
                self.logger.info(f"🔍 検査対象content: '{content}'")
                
                if meal_count > schedule_count:
                    self.logger.info(f"🔍 食事記録確認文脈検出: {meal_count}個のキーワード一致（直前メッセージのみ）")
                    return "meal_record"
                elif schedule_count > meal_count:
                    self.logger.info(f"🔍 スケジュール確認文脈検出: {schedule_count}個のキーワード一致（直前メッセージのみ）")
                    return "schedule_record"
                elif schedule_count > 0:  # 同数の場合はスケジュール優先（新機能のため）
                    self.logger.info(f"🔍 スケジュール確認文脈検出: {schedule_count}個のキーワード一致（同数につき優先）")
                    return "schedule_record"
                elif meal_count > 0:
                    self.logger.info(f"🔍 食事記録確認文脈検出: {meal_count}個のキーワード一致（直前メッセージのみ）")
                    return "meal_record"
        
        self.logger.info("🔍 確認文脈タイプ判定: キーワード一致なし、generalを返す")
        return "general"

    def get_strategy_name(self) -> str:
        """戦略名取得"""
        return "IntentBasedRouting"
