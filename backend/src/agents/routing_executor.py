"""RoutingExecutor - ルーティング実行とエージェント実行管理

ルーティング決定に基づくエージェント実行、フォールバック処理を担当
"""

import datetime
import json
import logging
import re
import time

from google.adk.runners import Runner
from google.genai.types import Content, Part
from src.agents.constants import (
    AGENT_DISPLAY_NAMES,
    AGENT_KEYWORDS,
    AGENT_RESPONSE_PATTERNS,
    ERROR_INDICATORS,
    EXPLICIT_SEARCH_FLAGS,
    FALLBACK_AGENT_PRIORITY,
)
from src.agents.message_processor import MessageProcessor
from src.agents.routing_strategy import RoutingStrategy


class RoutingExecutor:
    """ルーティング実行システム

    責務:
    - ルーティング決定に基づくエージェント実行
    - 専門家への自動ルーティング
    - フォールバック処理
    - レスポンス品質検証
    """

    def __init__(
        self,
        logger: logging.Logger,
        routing_strategy: RoutingStrategy,
        message_processor: MessageProcessor,
        composition_root = None,
        app_name: str = "GenieUs",
    ):
        """RoutingExecutor初期化

        Args:
            logger: DIコンテナから注入されるロガー
            routing_strategy: ルーティング戦略
            message_processor: メッセージプロセッサー
            composition_root: CompositionRoot（重複初期化回避用）
            app_name: アプリケーション名

        """
        self.logger = logger
        self.routing_strategy = routing_strategy
        self.message_processor = message_processor
        self._composition_root = composition_root
        self._app_name = app_name

    async def execute_with_routing(
        self,
        message: str,
        user_id: str,
        session_id: str,
        runners: dict[str, Runner],
        session_service,
        enhanced_message: str,
        conversation_history: list | None = None,
        family_info: dict | None = None,
        agent_type: str = "auto",
        # 画像・マルチモーダル対応パラメータ追加
        has_image: bool = False,
        message_type: str = "text",
        image_path: str = None,
        multimodal_context: dict = None,
    ) -> tuple[str, dict, list]:
        """ルーティングを含むエージェント実行

        Returns:
            Tuple[response, agent_info, routing_path]

        """
        routing_path = []
        agent_info = {}

        try:
            # エージェント選択
            routing_start_time = time.time()

            if agent_type == "auto":
                selected_agent_type = self._determine_agent_type(
                    message, conversation_history, family_info, has_image, message_type
                )
                self.logger.info(f"🔍 _determine_agent_type結果: '{selected_agent_type}'")
                self._log_routing_decision(message, selected_agent_type, "auto_routing")
            elif agent_type in ["sequential", "parallel"]:
                selected_agent_type = agent_type
                self._log_routing_decision(message, selected_agent_type, "explicit_routing")
            else:
                selected_agent_type = agent_type
                self._log_routing_decision(message, selected_agent_type, "direct_routing")

            routing_duration = time.time() - routing_start_time
            self.logger.info(
                f"🎯 ルーティング決定: {selected_agent_type} (判定時間: {routing_duration:.3f}s)",
            )
            self.logger.info(f"🔍 デバッグ: selected_agent_type='{selected_agent_type}', type={type(selected_agent_type)}")

            # デバッグ: 特別処理前の値確認
            self.logger.info(f"🔍 特別処理前: selected_agent_type='{selected_agent_type}' (type: {type(selected_agent_type)})")
            
            # ルーティング妥当性チェック
            if not self._validate_routing_decision(message, selected_agent_type):
                self.logger.warning(f"⚠️ ルーティング妥当性警告: {selected_agent_type} が適切でない可能性")
                corrected_agent = self._auto_correct_routing(message, selected_agent_type)
                if corrected_agent != selected_agent_type:
                    self.logger.info(f"🔧 ルーティング自動修正: {selected_agent_type} → {corrected_agent}")
                    selected_agent_type = corrected_agent
                else:
                    self.logger.info(f"✅ ルーティング自動修正不要: {selected_agent_type} をそのまま使用")
            
            # デバッグ: 特別処理直前の値確認  
            self.logger.info(f"🔍 特別処理直前: selected_agent_type='{selected_agent_type}' (type: {type(selected_agent_type)})")

            # 🍽️ **特別処理**: meal_record_api の場合は直接API実行
            if selected_agent_type == "meal_record_api":
                self.logger.info(f"🎯 meal_record_api実行: 会話履歴から食事記録作成")
                api_response = await self._execute_meal_record_api(
                    conversation_history, user_id, session_id, family_info
                )
                return api_response, {"agent_id": "meal_record_api", "agent_name": "食事記録API", "display_name": "食事記録作成"}, routing_path
            
            # 📅 **特別処理**: schedule_record_api の場合は直接API実行
            if selected_agent_type == "schedule_record_api":
                self.logger.info(f"🎯 schedule_record_api実行開始: 会話履歴からスケジュール記録作成")
                self.logger.info(f"🔍 selected_agent_type確認: {selected_agent_type}")
                api_response = await self._execute_schedule_record_api(
                    conversation_history, user_id, session_id, family_info
                )
                self.logger.info(f"✅ schedule_record_api実行完了: {len(api_response) if api_response else 0}文字")
                return api_response, {"agent_id": "schedule_record_api", "agent_name": "スケジュール記録API", "display_name": "スケジュール記録作成"}, routing_path

            # Runner取得
            if selected_agent_type not in runners:
                self.logger.warning(f"⚠️ {selected_agent_type} Runnerが見つかりません。coordinatorを使用")
                selected_agent_type = "coordinator"

            runner = runners[selected_agent_type]

            # エージェント情報
            agent_info = {
                "agent_id": selected_agent_type,
                "agent_name": runner.agent.name,
                "display_name": AGENT_DISPLAY_NAMES.get(selected_agent_type, selected_agent_type),
                "model": getattr(runner.agent, "model", "unknown"),
                "has_tools": hasattr(runner.agent, "tools") and runner.agent.tools is not None,
            }

            # ルーティングパス記録
            routing_path.append(
                {
                    "step": "routing_decision",
                    "selected_agent": selected_agent_type,
                    "display_name": AGENT_DISPLAY_NAMES.get(selected_agent_type, selected_agent_type),
                    "timestamp": time.time(),
                },
            )

            self.logger.info(f"🚀 実行エージェント: {selected_agent_type} (Agent: {runner.agent.name})")
            self.logger.info(f"🔍 最終確認: selected_agent_type='{selected_agent_type}', runner.agent.name='{runner.agent.name}'")

            # セッション確保
            await self._ensure_session_exists(user_id, session_id, session_service)

            # 画像パス情報をログ出力
            if image_path:
                self.logger.info(f"🖼️ 画像パス受信: {len(image_path) if image_path else 0}文字")

            # エージェント実行
            content = Content(role="user", parts=[Part(text=enhanced_message)])
            response = await self._execute_agent(
                runner,
                user_id,
                session_id,
                content,
                selected_agent_type,
            )

            # コーディネーターの場合、専門家ルーティングチェック
            if selected_agent_type == "coordinator":
                specialist_result = await self._check_and_route_to_specialist(
                    message,
                    response,
                    user_id,
                    session_id,
                    runners,
                    session_service,
                    conversation_history,
                    family_info,
                )

                if specialist_result:
                    specialist_response, specialist_agent_id = specialist_result

                    # ルーティングパス更新
                    routing_path.append(
                        {
                            "step": "specialist_routing",
                            "agent": specialist_agent_id,
                            "display_name": AGENT_DISPLAY_NAMES.get(specialist_agent_id, "専門家"),
                            "timestamp": time.time(),
                        },
                    )

                    return specialist_response, agent_info, routing_path

            return response, agent_info, routing_path

        except Exception as e:
            self.logger.error(f"エージェント実行エラー: {e}")
            return (
                f"申し訳ございません。システムエラーが発生しました: {e!s}",
                agent_info,
                routing_path,
            )

    async def _execute_agent(
        self,
        runner: Runner,
        user_id: str,
        session_id: str,
        content: Content,
        agent_type: str,
    ) -> str:
        """エージェント実行"""
        events = []
        tool_used = False

        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=content,
        ):
            events.append(event)

            # ツール使用検出
            if hasattr(event, "actions") and event.actions:
                tool_used = True
                self._log_tool_usage(event, agent_type)

            # レスポンス内容ログ
            if hasattr(event, "content") and event.content:
                self._log_response_content(event.content, agent_type)

        self.logger.info(
            f"🔧 {agent_type} ツール使用結果: {'使用された' if tool_used else '使用されなかった'}",
        )

        # レスポンス抽出
        if events and hasattr(events[-1], "content") and events[-1].content:
            return self._extract_response_text(events[-1].content)
        else:
            raise Exception("No response from agent")

    def _determine_agent_type(
        self,
        message: str,
        conversation_history: list | None = None,
        family_info: dict | None = None,
        has_image: bool = False,
        message_type: str = "text",
    ) -> str:
        """ルーティング決定"""
        if not self.routing_strategy:
            raise ValueError("ルーティング戦略が設定されていません")

        # 🖼️ **最優先**: 画像添付検出（戦略に依存しない）
        if has_image or message_type == "image":
            self.logger.info(
                f"🎯 RoutingExecutor: 画像添付最優先検出 has_image={has_image}, message_type={message_type} → image_specialist"
            )
            return "image_specialist"

        # 🔍 **第2優先**: 明示的検索フラグの直接検出（戦略に依存しない）
        for search_flag in EXPLICIT_SEARCH_FLAGS:
            if search_flag.lower() in message.lower() or search_flag in message:
                self.logger.info(f"🎯 RoutingExecutor: 明示的検索フラグ第2優先検出 '{search_flag}' → search_specialist")
                return "search_specialist"

        agent_id, routing_info = self.routing_strategy.determine_agent(
            message, conversation_history, family_info, has_image, message_type
        )
        self.logger.info(
            f"🎯 戦略ルーティング: {agent_id} "
            f"(確信度: {routing_info.get('confidence', 0):.1%}, "
            f"理由: {routing_info.get('reasoning', 'なし')})",
        )

        # ADKモード時は強制マッピングを無効化（ADK標準ルーティングを尊重）
        if self.routing_strategy and hasattr(self.routing_strategy, "get_strategy_name"):
            strategy_name = self.routing_strategy.get_strategy_name()
            if "ADK" in strategy_name or "adk" in strategy_name.lower():
                self.logger.info(f"🎯 ADKモード: エージェント強制マッピング無効化, 選択エージェント='{agent_id}'を維持")
                return agent_id

        # 🍽️ **特例**: meal_record_api は直接API実行（確認応答処理のため）
        if agent_id == "meal_record_api":
            self.logger.info(f"🎯 meal_record_api直接実行: 確認応答による食事記録API呼び出し")
            return agent_id

        # 📅 **特例**: schedule_record_api は直接API実行（確認応答処理のため）
        if agent_id == "schedule_record_api":
            self.logger.info(f"🎯 schedule_record_api直接実行: 確認応答によるスケジュール記録API呼び出し")
            return agent_id

        # coordinatorではない専門エージェントが選ばれた場合は
        # 既存の動作を維持（coordinator経由）
        if agent_id != "coordinator" and agent_id not in ["parallel", "sequential"]:
            return "coordinator"
        return agent_id

    async def _check_and_route_to_specialist(
        self,
        original_message: str,
        coordinator_response: str,
        user_id: str,
        session_id: str,
        runners: dict[str, Runner],
        session_service,
        conversation_history: list | None = None,
        family_info: dict | None = None,
    ) -> tuple[str, str] | None:
        """コーディネーターのレスポンスから専門家紹介を検出し、自動ルーティング

        Returns:
            Optional[Tuple[response, specialist_agent_id]]

        """
        # ADKモード時は既存のパターンマッチングを無効化（ADK標準のtransfer_to_agent()を使用）
        if self.routing_strategy and hasattr(self.routing_strategy, "get_strategy_name"):
            strategy_name = self.routing_strategy.get_strategy_name()
            if "ADK" in strategy_name or "adk" in strategy_name.lower():
                self.logger.info("🎯 ADKモード検出: 既存パターンマッチング無効化、ADK標準transfer_to_agent()に委任")
                return None

        response_lower = coordinator_response.lower()

        # 専門家への紹介キーワードを検出
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

        keyword_match = any(keyword in response_lower for keyword in routing_keywords)

        # 元のメッセージが専門的な相談の場合は強制的にルーティング
        specialist_agent, routing_info = self.routing_strategy.determine_agent(original_message.lower())
        should_route_automatically = (
            specialist_agent and specialist_agent != "coordinator" and specialist_agent in runners
        )

        if keyword_match or should_route_automatically:
            if keyword_match:
                self.logger.info("🔄 コーディネーターが専門家紹介を提案、自動ルーティング開始")
            else:
                self.logger.info("🔄 専門的相談を検出、強制的に専門家ルーティング開始")

            # 専門家ルーティング実行
            specialist_response = await self._perform_specialist_routing(
                original_message,
                user_id,
                session_id,
                runners,
                session_service,
                conversation_history,
                family_info,
            )

            if specialist_response and specialist_response != "コーディネーターで直接対応いたします。":
                self.logger.info(f"✅ 専門家ルーティング成功: レスポンス長={len(specialist_response)}")
                # 専門家IDも返す
                specialist_id = self._determine_specialist_from_message(original_message)
                return specialist_response, specialist_id
            else:
                self.logger.warning("⚠️ 専門家ルーティングが失敗またはフォールバック")

        return None

    async def _perform_specialist_routing(
        self,
        message: str,
        user_id: str,
        session_id: str,
        runners: dict[str, Runner],
        session_service,
        conversation_history: list | None = None,
        family_info: dict | None = None,
    ) -> str:
        """強化されたスペシャリストルーティング"""
        # 戦略パターンを使用してエージェントを決定
        agent_id, routing_info = self.routing_strategy.determine_agent(
            message,
            conversation_history,
            family_info,
        )

        # 🍽️ **特別処理**: meal_record_api の場合は直接API実行
        if agent_id == "meal_record_api":
            self.logger.info(f"🎯 _perform_specialist_routing: meal_record_api実行開始")
            api_response = await self._execute_meal_record_api(
                conversation_history, user_id, session_id, family_info
            )
            self.logger.info(f"✅ _perform_specialist_routing: meal_record_api実行完了")
            return api_response

        # 📅 **特別処理**: schedule_record_api の場合は直接API実行
        if agent_id == "schedule_record_api":
            self.logger.info(f"🎯 _perform_specialist_routing: schedule_record_api実行開始")
            api_response = await self._execute_schedule_record_api(
                conversation_history, user_id, session_id, family_info
            )
            self.logger.info(f"✅ _perform_specialist_routing: schedule_record_api実行完了")
            return api_response

        # エージェントが存在する場合はルーティング
        if agent_id and agent_id in runners:
            self.logger.info(
                f"🔄 専門エージェントへルーティング: {AGENT_DISPLAY_NAMES.get(agent_id, agent_id)}",
            )
            return await self._route_to_specific_agent_with_fallback(
                agent_id,
                message,
                user_id,
                session_id,
                runners,
                session_service,
                conversation_history,
                family_info,
            )

        # フォールバック階層
        for fallback_agent in FALLBACK_AGENT_PRIORITY:
            if fallback_agent in runners:
                self.logger.info(
                    f"🔄 フォールバックルーティング: {AGENT_DISPLAY_NAMES.get(fallback_agent, fallback_agent)}",
                )
                return await self._route_to_specific_agent_with_fallback(
                    fallback_agent,
                    message,
                    user_id,
                    session_id,
                    runners,
                    session_service,
                    conversation_history,
                    family_info,
                )

        # 最終フォールバック
        self.logger.warning("⚠️ 全ての専門エージェントが利用できません。コーディネーターで対応します。")
        return "コーディネーターで直接対応いたします。"

    async def _route_to_specific_agent_with_fallback(
        self,
        agent_id: str,
        message: str,
        user_id: str,
        session_id: str,
        runners: dict[str, Runner],
        session_service,
        conversation_history: list | None = None,
        family_info: dict | None = None,
        retry_count: int = 0,
        max_retries: int = 2,
    ) -> str:
        """フォールバック機能付き専門エージェント実行"""
        if agent_id not in runners:
            self.logger.error(f"❌ エージェント {agent_id} が存在しません")
            return await self._execute_fallback_agent(
                message,
                user_id,
                session_id,
                runners,
                session_service,
                conversation_history,
                family_info,
            )

        try:
            # 専門エージェント実行
            runner = runners[agent_id]
            await self._ensure_session_exists(user_id, session_id, session_service)

            # MessageProcessorを使用してコンテキスト付きメッセージを作成
            enhanced_message = self.message_processor.create_message_with_context(
                message,
                conversation_history,
                family_info,
            )
            content = Content(role="user", parts=[Part(text=enhanced_message)])

            # 実行
            response = await self._execute_agent(
                runner,
                user_id,
                session_id,
                content,
                agent_id,
            )

            # レスポンス品質検証
            if self._validate_agent_response(response, agent_id, message):
                self.logger.info(f"✅ {agent_id} レスポンス検証成功")
                return response
            else:
                self.logger.warning(f"⚠️ {agent_id} レスポンス品質不良、リトライ実行")
                if retry_count < max_retries:
                    return await self._route_to_specific_agent_with_fallback(
                        agent_id,
                        message,
                        user_id,
                        session_id,
                        runners,
                        session_service,
                        conversation_history,
                        family_info,
                        retry_count + 1,
                        max_retries,
                    )
                else:
                    self.logger.error(f"❌ {agent_id} 最大リトライ回数到達、フォールバック実行")
                    return await self._execute_fallback_agent(
                        message,
                        user_id,
                        session_id,
                        runners,
                        session_service,
                        conversation_history,
                        family_info,
                    )

        except Exception as e:
            self.logger.error(f"❌ 専門エージェント({agent_id})実行エラー: {e}")
            if retry_count < max_retries:
                self.logger.info(f"🔄 リトライ実行 ({retry_count + 1}/{max_retries})")
                return await self._route_to_specific_agent_with_fallback(
                    agent_id,
                    message,
                    user_id,
                    session_id,
                    runners,
                    session_service,
                    conversation_history,
                    family_info,
                    retry_count + 1,
                    max_retries,
                )
            else:
                return await self._execute_fallback_agent(
                    message,
                    user_id,
                    session_id,
                    runners,
                    session_service,
                    conversation_history,
                    family_info,
                )

    async def _execute_fallback_agent(
        self,
        message: str,
        user_id: str,
        session_id: str,
        runners: dict[str, Runner],
        session_service,
        conversation_history: list | None = None,
        family_info: dict | None = None,
    ) -> str:
        """フォールバックエージェント実行"""
        # 安全なフォールバック順序
        for fallback_agent in FALLBACK_AGENT_PRIORITY[:3]:
            if fallback_agent in runners:
                try:
                    self.logger.info(f"🔄 フォールバックエージェント実行: {fallback_agent}")
                    runner = runners[fallback_agent]
                    await self._ensure_session_exists(user_id, session_id, session_service)

                    enhanced_message = self._create_simple_context_message(
                        message,
                        conversation_history,
                        family_info,
                    )
                    content = Content(role="user", parts=[Part(text=enhanced_message)])

                    response = await self._execute_agent(
                        runner,
                        user_id,
                        session_id,
                        content,
                        fallback_agent,
                    )

                    if response and len(response.strip()) > 10:
                        self.logger.info(f"✅ フォールバック成功: {fallback_agent}")
                        return f"【{AGENT_DISPLAY_NAMES.get(fallback_agent, fallback_agent)}より】\n{response}"

                except Exception as e:
                    self.logger.error(f"❌ フォールバックエージェント({fallback_agent})エラー: {e}")
                    continue

        # 最終的なエラーメッセージ
        self.logger.error("❌ 全てのフォールバック手段が失敗しました")
        return (
            "申し訳ございません。現在システムで問題が発生しており、"
            "専門的なアドバイスを提供できません。しばらく時間をおいてから"
            "再度お試しいただくか、緊急の場合は直接医療機関にご相談ください。"
        )

    def _validate_agent_response(
        self,
        response: str,
        agent_id: str,
        original_message: str,
    ) -> bool:
        """エージェントレスポンスの妥当性検証"""
        if not response or len(response.strip()) < 20:
            return False

        # 🚨 **検索エージェントは特別扱い** - 丁寧語を含むため除外
        if agent_id == "search_specialist":
            self.logger.info(f"✅ search_specialist は品質チェックを簡素化")
            # 検索結果が含まれているかの基本チェックのみ
            return len(response.strip()) > 50

        # エージェント固有の妥当性チェック
        if agent_id in AGENT_RESPONSE_PATTERNS:
            patterns = AGENT_RESPONSE_PATTERNS[agent_id]
            if not any(pattern in response for pattern in patterns):
                self.logger.warning(
                    f"⚠️ {agent_id} 専門性関連キーワードが不足: {patterns}",
                )
                return False

        # 一般的品質チェック
        if any(indicator in response for indicator in ERROR_INDICATORS):
            self.logger.warning(f"⚠️ エラー指標を含むレスポンス: {ERROR_INDICATORS}")
            return False

        return True

    def _validate_routing_decision(self, message: str, selected_agent: str) -> bool:
        """ルーティング決定の妥当性検証"""
        message_lower = message.lower()

        # 🚨 **特別なAPIエージェントは常に有効**
        if selected_agent in ["meal_record_api", "schedule_record_api"]:
            self.logger.info(f"✅ API実行エージェント({selected_agent})は妥当性チェックをパス")
            return True

        # 明らかに不適切なルーティングを検出
        inappropriate_routing = {
            "sleep_specialist": ["食事", "離乳食", "栄養", "食べない"],
            "nutrition_specialist": ["夜泣き", "寝ない", "睡眠", "寝かしつけ"],
            "health_specialist": ["遊び", "おもちゃ", "知育"],
            "play_learning_specialist": ["熱", "病気", "体調不良"],
        }

        if selected_agent in inappropriate_routing:
            inappropriate_keywords = inappropriate_routing[selected_agent]
            if any(keyword in message_lower for keyword in inappropriate_keywords):
                matched = [kw for kw in inappropriate_keywords if kw in message_lower]
                self.logger.warning(
                    f"⚠️ 不適切ルーティング検出: {selected_agent} に {matched} が含まれる",
                )
                return False

        return True

    def _auto_correct_routing(self, message: str, original_agent: str) -> str:
        """自動ルーティング修正"""
        message_lower = message.lower()

        # 🚨 **特別なAPIエージェントは修正しない**
        if original_agent in ["meal_record_api", "schedule_record_api"]:
            self.logger.info(f"🔒 API実行エージェント({original_agent})は自動修正をスキップ")
            return original_agent

        # 強制ルーティングをまず確認
        force_agent = self.routing_strategy._check_force_routing(message_lower)
        if force_agent:
            return force_agent

        # 決定論的再ルーティング
        corrected_agent, routing_info = self.routing_strategy._determine_specialist_agent(message_lower)
        if corrected_agent and corrected_agent != "coordinator":
            return "coordinator"  # コーディネーター経由

        # フォールバック
        return "coordinator"

    def _determine_specialist_from_message(self, message: str) -> str:
        """メッセージから専門家IDを判定"""
        message_lower = message.lower()

        # 各専門エージェントのキーワードマッチング
        for agent_id, keywords in AGENT_KEYWORDS.items():
            if any(keyword in message_lower for keyword in keywords):
                return agent_id

        return "nutrition_specialist"  # デフォルト

    async def _ensure_session_exists(
        self,
        user_id: str,
        session_id: str,
        session_service,
    ) -> None:
        """セッション存在確認・作成"""
        try:
            await session_service.get_session(self._app_name, user_id, session_id)
        except Exception:
            await session_service.create_session(
                app_name=self._app_name,
                user_id=user_id,
                session_id=session_id,
            )

    def _create_simple_context_message(
        self,
        message: str,
        conversation_history: list | None = None,
        family_info: dict | None = None,
    ) -> str:
        """簡易版コンテキスト付きメッセージ作成"""
        # MessageProcessorの代替実装（フォールバック用）
        parts = []

        if family_info:
            # 簡易版でも基本的な家族情報を含める
            children = family_info.get("children", [])
            parent_name = family_info.get("parent_name", "")
            if parent_name:
                parts.append(f"【保護者: {parent_name}さん】")
            if children:
                child_summary = f"{len(children)}人のお子さん"
                if children and children[0].get("name"):
                    child_summary += f"（{children[0]['name']}さんなど）"
                parts.append(f"【お子さん: {child_summary}】")

        if conversation_history:
            parts.append(f"【会話履歴: {len(conversation_history)}件】")

        parts.append(f"【現在のメッセージ】\n{message}")

        return "\n".join(parts)

    def _extract_response_text(self, response_content) -> str:
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

    def _log_routing_decision(
        self,
        message: str,
        selected_agent: str,
        routing_type: str,
    ) -> None:
        """ルーティング決定の詳細ログ"""
        message_preview = message[:50] + "..." if len(message) > 50 else message
        agent_display = AGENT_DISPLAY_NAMES.get(selected_agent, selected_agent)

        self.logger.info(
            f"📋 ルーティング詳細 - タイプ: {routing_type}, 選択: {agent_display}, メッセージ: '{message_preview}'",
        )

    def _log_tool_usage(self, event, agent_type: str) -> None:
        """ツール使用ログ"""
        try:
            action_count = len(list(event.actions)) if hasattr(event.actions, "__iter__") else 1
            self.logger.info(f"🔧 {agent_type} ツール実行検出: {action_count}個のアクション")

            for i, action in enumerate(event.actions):
                action_type = type(action).__name__
                action_str = str(action)

                # ツール名を抽出して明確にログ出力
                tool_name = self._extract_tool_name(action_str)
                if tool_name:
                    self.logger.info(f"🛠️ ツール実行#{i + 1}: {tool_name} ({action_type})")
                else:
                    self.logger.info(f"📋 アクション#{i + 1}: {action_type}")
                    # デバッグ：ツール名が抽出できない場合の詳細情報
                    self.logger.debug(f"🔍 ツール名抽出失敗 - アクション: {action_str[:200]}")

                # アクション内容を詳細にログ出力
                if len(action_str) > 100:
                    self.logger.info(f"📄 アクション内容: {action_str[:500]}...")
                else:
                    self.logger.info(f"📄 アクション内容: {action_str}")

                # 特別なアクションタイプの場合、追加情報をログ
                if hasattr(action, "__len__") and len(action) >= 2:
                    try:
                        action_name, action_data = action[0], action[1]
                        if action_name in ["function_call", "tool_call"]:
                            self.logger.info(f"🔧 関数呼び出し検出: {action_name} -> {action_data}")
                    except Exception:
                        pass
        except Exception as e:
            self.logger.info(f"🔧 ツール実行検出: アクションあり (詳細取得エラー: {e})")

    def _extract_tool_name(self, action_str: str) -> str:
        """アクション文字列からツール名を抽出"""
        try:
            import re

            # より詳細なパターンマッチングを実行
            # 1. FunctionCall パターンを検出
            if "function_call" in action_str.lower():
                # name パターンで関数名を抽出（複数パターン対応）
                patterns = [
                    r"name['\"]?\s*:\s*['\"]?([a-zA-Z_]+)['\"]?",  # name: "function_name"
                    r"'name':\s*'([a-zA-Z_]+)'",  # 'name': 'function_name'
                    r'"name":\s*"([a-zA-Z_]+)"',  # "name": "function_name"
                ]

                for pattern in patterns:
                    match = re.search(pattern, action_str)
                    if match:
                        function_name = match.group(1)
                        # ツール名のマッピング
                        tool_mapping = {
                            "get_family_information": "family_info",
                            "analyze_child_image": "image_analysis",
                            "analyze_child_voice": "voice_analysis",
                            "manage_child_files": "file_management",
                            "manage_child_records": "record_management",
                            "search_with_history": "google_search",
                            "google_search": "google_search",  # 直接の場合も対応
                        }
                        return tool_mapping.get(function_name, function_name)

            # 2. アクションタイプから推測（フォールバック）
            action_lower = action_str.lower()
            if "search" in action_lower:
                return "google_search"
            elif "family" in action_lower or "parent" in action_lower:
                return "family_info"
            elif "image" in action_lower or "photo" in action_lower:
                return "image_analysis"
            elif "voice" in action_lower or "audio" in action_lower:
                return "voice_analysis"
            elif "file" in action_lower:
                return "file_management"
            elif "record" in action_lower:
                return "record_management"

            return ""
        except Exception as e:
            self.logger.debug(f"ツール名抽出エラー: {e}")
            return ""

    def _log_response_content(self, content, agent_type: str) -> None:
        """レスポンス内容ログ"""
        if hasattr(content, "parts") and content.parts:
            for i, part in enumerate(content.parts):
                if hasattr(part, "function_response"):
                    response_str = str(part.function_response)
                    # ツール名を抽出してレスポンスを分かりやすく
                    tool_name = self._extract_tool_name_from_response(response_str)
                    if tool_name:
                        self.logger.info(
                            f"✅ {tool_name}ツール結果#{i + 1}: {response_str[:300]}...",
                        )
                    else:
                        self.logger.info(
                            f"🔧 ツールレスポンス#{i + 1}: {response_str[:500]}...",
                        )
                elif hasattr(part, "text") and len(str(part.text)) > 0:
                    self.logger.info(
                        f"💬 {agent_type} 文章#{i + 1}: {str(part.text)[:200]}...",
                    )

    def _extract_tool_name_from_response(self, response_str: str) -> str:
        """レスポンス文字列からツール名を抽出"""
        try:
            # family_data や success などのキーワードからツール推定
            if "family_data" in response_str or "parent_name" in response_str:
                return "family_info"
            elif "detected_items" in response_str or "emotion" in response_str:
                return "image_analysis"
            elif "search_results" in response_str or "search_metadata" in response_str:
                return "google_search"
            elif "voice_analysis" in response_str:
                return "voice_analysis"
            elif "file_operation" in response_str:
                return "file_management"
            elif "record_operation" in response_str:
                return "record_management"
            return ""
        except Exception:
            return ""

    async def _execute_meal_record_api(
        self,
        conversation_history: list | None,
        user_id: str,
        session_id: str,
        family_info: dict | None = None,
    ) -> str:
        """食事記録API直接実行
        
        Args:
            conversation_history: 会話履歴（画像解析結果を含む）
            user_id: ユーザーID
            session_id: セッションID
            family_info: 家族情報
            
        Returns:
            str: 食事記録作成結果メッセージ
        """
        try:
            self.logger.info("🍽️ 食事記録API実行開始: 会話履歴から画像解析結果を抽出")
            
            # 会話履歴から画像解析結果を抽出
            image_analysis_result = await self._extract_image_analysis_from_history(conversation_history)
            
            if not image_analysis_result:
                self.logger.warning("⚠️ 会話履歴に画像解析結果が見つかりません")
                return "申し訳ありません。画像解析結果が見つからないため、食事記録を作成できませんでした。"
            
            # 家族情報から子供情報を取得
            child_info = self._extract_child_info(family_info)
            
            # 食事記録データを構築
            meal_record_data = self._build_meal_record_data(image_analysis_result, child_info)
            
            # 食事記録API呼び出し（実際のAPI呼び出しをシミュレート）
            record_result = await self._call_meal_record_api(meal_record_data)
            
            if record_result.get("success"):
                self.logger.info(f"✅ 食事記録作成成功: {record_result.get('meal_id')}")
                
                # 日時を読みやすい形式にフォーマット
                from datetime import datetime
                timestamp_str = meal_record_data.get('timestamp', '不明')
                formatted_datetime = timestamp_str
                try:
                    if timestamp_str != '不明':
                        dt = datetime.fromisoformat(timestamp_str.replace('Z', ''))
                        formatted_datetime = dt.strftime('%Y年%m月%d日 %H:%M')
                except:
                    formatted_datetime = timestamp_str
                
                # 検出された食品
                detected_foods = meal_record_data.get('detected_foods', [])
                foods_text = ', '.join(detected_foods) if detected_foods else '記録なし'
                
                # 栄養情報
                nutrition_info = meal_record_data.get('nutrition_info', {})
                calories = nutrition_info.get('estimated_calories', 0)
                
                # レスポンス生成
                response_parts = [
                    "✅ **食事記録を作成しました！**",
                    "",
                    "🍽️ **記録詳細**",
                    f"📋 **食事名**: {meal_record_data.get('meal_name', '不明')}",
                    f"🕐 **記録日時**: {formatted_datetime}",
                    f"🥗 **検出された食品**: {foods_text}",
                    f"⚡ **推定カロリー**: {calories}kcal" if calories > 0 else "",
                    "",
                    "📊 **栄養バランス**",
                    f"• タンパク質: {nutrition_info.get('protein', 0)}g",
                    f"• 炭水化物: {nutrition_info.get('carbs', 0)}g", 
                    f"• 脂質: {nutrition_info.get('fat', 0)}g",
                    "",
                    "✅ 食事記録がデータベースに保存されました！お疲れ様でした！"
                ]
                
                return "\n".join([part for part in response_parts if part])  # 空行を除外
            else:
                self.logger.error(f"❌ 食事記録作成失敗: {record_result.get('error')}")
                return f"申し訳ありません。食事記録の作成中にエラーが発生しました: {record_result.get('error', '不明なエラー')}"
                
        except Exception as e:
            self.logger.error(f"❌ 食事記録API実行エラー: {e}")
            return f"申し訳ありません。食事記録作成中にシステムエラーが発生しました: {e!s}"

    async def _extract_image_analysis_from_history(self, conversation_history: list | None) -> dict | None:
        """会話履歴から画像解析結果を抽出（Gemini API使用）
        
        Args:
            conversation_history: 会話履歴
            
        Returns:
            dict | None: 画像解析結果データ
        """
        if not conversation_history:
            return None
            
        # 最新の画像解析結果を探す
        image_analysis_content = None
        for message in reversed(conversation_history):
            role = message.get("role")
            content = message.get("content", "")
            
            # エージェントからのメッセージ（genie役割またはNone/未指定）で画像解析結果を探す
            if role == "genie" or role is None or role == "":
                # 画像解析結果の特徴的なキーワードを検出
                image_analysis_indicators = [
                    "お食事中のお写真",
                    "拝見しましたところ",
                    "お食事は",
                    "豆腐やトマト",
                    "美味しそうで",
                    "食べていたのでしょうね",
                    "画像を分析",
                    "写真を見て",
                    "分析結果",
                    "お写真からは",
                    "この献立は",
                    "栄養・食事のジーニー",
                    "食事管理",
                    "食事記録"
                ]
                
                # 画像解析または食事関連の内容が含まれているかチェック
                for indicator in image_analysis_indicators:
                    if indicator in content:
                        image_analysis_content = content
                        self.logger.info(f"🔍 画像解析結果発見: '{indicator}' が含まれる応答")
                        break
                
                if image_analysis_content:
                    break
        
        if not image_analysis_content:
            self.logger.warning("⚠️ 会話履歴に画像解析結果が見つかりません")
            return None
        
        # Gemini APIを使用して画像解析結果を構造化
        try:
            return await self._structure_image_analysis_with_gemini(image_analysis_content)
        except Exception as e:
            self.logger.warning(f"⚠️ Gemini API構造化に失敗、フォールバックを使用: {e}")
            return self._extract_from_text(image_analysis_content)

    def _extract_from_text(self, content: str) -> dict:
        """テキストから食事情報を抽出（フォールバック）
        
        Args:
            content: メッセージ内容
            
        Returns:
            dict: 抽出された食事情報
        """
        # 基本的な食品キーワードを検索
        food_keywords = ["ご飯", "パン", "麺", "肉", "魚", "野菜", "果物", "おかず", "スープ", "サラダ"]
        detected_foods = [food for food in food_keywords if food in content]
        
        return {
            "detected_items": detected_foods or ["不明な食品"],
            "analysis_confidence": 0.5,
            "meal_type": "main_meal",
            "extracted_from": "text_fallback"
        }

    async def _structure_image_analysis_with_gemini(self, image_analysis_content: str) -> dict:
        """Gemini APIを使用して画像解析結果を構造化
        
        Args:
            image_analysis_content: 画像解析の自然言語レスポンス
            
        Returns:
            dict: 構造化された画像解析結果
        """
        try:
            # Vertex AI Gemini APIを使用してデータを構造化
            import os

            import vertexai
            from vertexai.generative_models import GenerativeModel

            # Vertex AI初期化
            project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "blog-sample-381923")
            location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
            vertexai.init(project=project_id, location=location)
            
            model = GenerativeModel("gemini-2.5-flash")
            
            # 構造化プロンプト
            structure_prompt = f"""
以下の画像解析レスポンスから、食事記録用の構造化データを抽出してください。
必ずJSON形式で応答し、以下の形式に従ってください：

{{
    "detected_items": ["食品名1", "食品名2", ...],
    "meal_type": "breakfast|lunch|dinner|snack",
    "estimated_portions": {{"食品名": "小盛り|普通|大盛り", ...}},
    "nutritional_notes": "栄養に関するコメント",
    "analysis_confidence": 0.0-1.0の数値,
    "meal_description": "食事の簡潔な説明"
}}

画像解析レスポンス:
{image_analysis_content}

JSONのみを返してください。余計な説明は不要です。
"""

            # API呼び出し
            response = model.generate_content(structure_prompt)
            response_text = response.text.strip()
            
            # JSON部分を抽出
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                structured_data = json.loads(json_str)
                
                self.logger.info(f"✅ Gemini API構造化成功: {len(structured_data.get('detected_items', []))}個の食品を検出")
                return structured_data
            else:
                raise ValueError("JSONレスポンスが見つかりません")
                
        except Exception as e:
            self.logger.error(f"❌ Gemini API構造化エラー: {e}")
            # フォールバック: 基本的な構造化データを返す
            return {
                "detected_items": ["画像から検出された食品"],
                "meal_type": "main_meal",
                "estimated_portions": {},
                "nutritional_notes": "Gemini API構造化に失敗しました",
                "analysis_confidence": 0.3,
                "meal_description": "画像解析レスポンスから抽出",
                "original_content": image_analysis_content[:200] + "..." if len(image_analysis_content) > 200 else image_analysis_content
            }

    def _extract_child_info(self, family_info: dict | None) -> dict:
        """家族情報から子供情報を抽出
        
        Args:
            family_info: 家族情報
            
        Returns:
            dict: 子供情報
        """
        if not family_info or not family_info.get("children"):
            return {"child_id": "default_child", "name": "お子さん", "age": "不明"}
        
        # 最初の子供の情報を使用
        child = family_info["children"][0]
        return {
            "child_id": child.get("name", "default_child"),
            "name": child.get("name", "お子さん"),
            "age": child.get("age", "不明"),
            "birth_date": child.get("birth_date", "")
        }

    def _build_meal_record_data(self, image_analysis: dict, child_info: dict) -> dict:
        """食事記録データを構築
        
        Args:
            image_analysis: 画像解析結果
            child_info: 子供情報
            
        Returns:
            dict: 食事記録データ
        """
        
        detected_foods = image_analysis.get("detected_items", [])
        
        return {
            "child_id": child_info.get("child_id", "default_child"),
            "meal_name": f"{child_info.get('name', 'お子さん')}の食事記録",
            "meal_type": "snack",  # デフォルトはおやつ
            "detected_foods": detected_foods,
            "timestamp": datetime.datetime.now().isoformat(),  # meal_date → timestamp
            "nutrition_info": {
                "estimated_calories": len(detected_foods) * 50,  # 簡易推定
                "food_variety": len(detected_foods),
                "protein": len(detected_foods) * 2,  # 簡易推定
                "carbs": len(detected_foods) * 8,    # 簡易推定
                "fat": len(detected_foods) * 1       # 簡易推定
            },
            "detection_source": "image_ai",  # analysis_source → detection_source
            "confidence": image_analysis.get("analysis_confidence", 0.8),
            "notes": f"画像解析により検出された食品: {', '.join(detected_foods)}"
        }

    async def _call_meal_record_api(self, meal_data: dict) -> dict:
        """食事記録API呼び出し（実際のデータベース保存）
        
        Args:
            meal_data: 食事記録データ
            
        Returns:
            dict: API応答結果
        """
        try:
            self.logger.info(f"🍽️ 食事記録API呼び出し: {meal_data}")
            
            # Composition Rootから実際のMealRecordUseCaseを取得（重複初期化回避）
            if self._composition_root:
                meal_record_usecase = self._composition_root._usecases.get("meal_record")
            else:
                # フォールバック: 新規作成（非推奨パターン）
                from src.di_provider.composition_root import CompositionRootFactory
                composition_root = CompositionRootFactory.create()
                meal_record_usecase = composition_root._usecases.get("meal_record")
            
            if not meal_record_usecase:
                self.logger.error("❌ MealRecordUseCaseが利用できません")
                return {
                    "success": False,
                    "error": "食事記録機能が利用できません（SQLiteモードでない可能性があります）"
                }
            
            # MealRecordRequestオブジェクトを作成
            from datetime import datetime

            from src.application.usecases.meal_record_usecase import (
                CreateMealRecordRequest,
            )
            
            # timestampの処理
            timestamp = datetime.now()
            if meal_data.get("timestamp"):
                try:
                    timestamp = datetime.fromisoformat(meal_data.get("timestamp").replace("Z", "+00:00"))
                except Exception:
                    timestamp = datetime.now()
            
            meal_record_request = CreateMealRecordRequest(
                child_id=meal_data.get("child_id", "default_child"),
                meal_name=meal_data.get("meal_name", "食事記録"),
                meal_type=meal_data.get("meal_type", "snack"),
                timestamp=timestamp,
                detected_foods=meal_data.get("detected_foods", []),
                nutrition_info=meal_data.get("nutrition_info", {}),
                confidence=meal_data.get("confidence", 0.8),
                detection_source=meal_data.get("detection_source", "image_ai"),  # analysis_source → detection_source
                notes=meal_data.get("notes", "")
            )
            
            # データベースに実際に保存
            meal_record_response = await meal_record_usecase.create_meal_record(meal_record_request)
            
            if not meal_record_response.success:
                self.logger.error(f"❌ 食事記録作成失敗: {meal_record_response.error}")
                return {
                    "success": False,
                    "error": meal_record_response.error
                }
            
            meal_record = meal_record_response.meal_record
            meal_id = meal_record.get("id") if meal_record else "unknown"
            
            self.logger.info(f"✅ 実際のデータベース保存成功: {meal_id}")
            
            return {
                "success": True,
                "meal_id": meal_id,
                "message": "食事記録がデータベースに正常に保存されました",
                "record": meal_record
            }
            
        except Exception as e:
            self.logger.error(f"❌ 食事記録API呼び出しエラー: {e}")
            return {
                "success": False,
                "error": f"データベース保存エラー: {str(e)}"
            }

    async def _execute_schedule_record_api(
        self,
        conversation_history: list | None,
        user_id: str,
        session_id: str,
        family_info: dict | None = None,
    ) -> str:
        """スケジュール記録API直接実行
        
        Args:
            conversation_history: 会話履歴（スケジュール提案を含む）
            user_id: ユーザーID
            session_id: セッションID
            family_info: 家族情報
            
        Returns:
            str: スケジュール記録作成結果メッセージ
        """
        try:
            self.logger.info("📅 スケジュール記録API実行開始: 会話履歴からスケジュール情報を抽出")
            
            # 会話履歴からスケジュール提案を抽出
            schedule_proposal = await self._extract_schedule_proposal_from_history(conversation_history)
            
            if not schedule_proposal:
                self.logger.warning("⚠️ 会話履歴にスケジュール提案が見つかりません")
                return "申し訳ありません。スケジュール提案が見つからないため、予定を作成できませんでした。"
            
            # 家族情報から子供情報を取得
            child_info = self._extract_child_info(family_info)
            
            # スケジュール記録データを構築
            schedule_record_data = self._build_schedule_record_data(schedule_proposal, child_info, user_id)
            
            # スケジュール記録API呼び出し（実際のAPI呼び出し）
            record_result = await self._call_schedule_record_api(schedule_record_data)
            
            if record_result.get("success"):
                self.logger.info(f"✅ スケジュール記録作成成功: {record_result.get('schedule_id')}")
                
                # 日時を読みやすい形式にフォーマット
                from datetime import datetime
                start_datetime = schedule_record_data.get('start_datetime', '不明')
                formatted_datetime = start_datetime
                try:
                    if start_datetime != '不明':
                        dt = datetime.fromisoformat(start_datetime.replace('T', ' ').replace('Z', ''))
                        formatted_datetime = dt.strftime('%Y年%m月%d日 %H:%M')
                except:
                    formatted_datetime = start_datetime
                
                # 内容を改行で整理
                description = schedule_record_data.get('description', '')
                notes = schedule_record_data.get('notes', '')
                
                # レスポンス生成
                response_parts = [
                    "✅ **予定を登録しました！**",
                    "",
                    "📅 **予定詳細**",
                    f"📋 **タイトル**: {schedule_record_data.get('title', '不明')}",
                    f"🕐 **日時**: {formatted_datetime}",
                    f"📍 **場所**: {schedule_record_data.get('location', '未定')}",
                    f"📝 **内容**: {description}" if description else "",
                    "",
                    "💡 **当日の準備**",
                    "• 健康保険証",
                    "• 乳児医療証", 
                    "• 母子手帳",
                    "• お薬手帳（服用中の薬がある場合）",
                    "",
                    "✅ 予定がカレンダーに保存され、リマインダーも設定済みです！"
                ]
                
                return "\n".join([part for part in response_parts if part])  # 空行を除外
            else:
                self.logger.error(f"❌ スケジュール記録作成失敗: {record_result.get('error')}")
                return f"申し訳ありません。予定の作成中にエラーが発生しました: {record_result.get('error', '不明なエラー')}"
                
        except Exception as e:
            self.logger.error(f"❌ スケジュール記録API実行エラー: {e}")
            return f"申し訳ありません。予定作成中にシステムエラーが発生しました: {e!s}"

    async def _extract_schedule_proposal_from_history(self, conversation_history: list | None) -> dict | None:
        """会話履歴からスケジュール提案を抽出（Gemini API使用）
        
        Args:
            conversation_history: 会話履歴
            
        Returns:
            dict | None: スケジュール提案データ
        """
        if not conversation_history:
            return None
            
        # 最新のスケジュール提案を探す
        schedule_proposal_content = None
        for message in reversed(conversation_history):
            role = message.get("role")
            content = message.get("content", "")
            
            # エージェントからのメッセージ（genie役割またはNone/未指定）でスケジュール提案を探す
            if role == "genie" or role is None or role == "":
                # スケジュール提案の特徴的なキーワードを検出
                schedule_proposal_indicators = [
                    "予定",
                    "スケジュール",
                    "診察",
                    "検診",
                    "健診",
                    "予約",
                    "カレンダー",
                    "日程",
                    "時間",
                    "午前",
                    "午後",
                    "来週",
                    "来月",
                    "明日",
                    "病院",
                    "クリニック",
                    "受診",
                    "通院",
                    "ワクチン",
                    "予防接種",
                    "健康管理のジーニー",
                    "次回の",
                    "忘れないように",
                    "記録しておく",
                    "リマインダー",
                    "お忘れなく",
                    "予定表",
                    "手帳"
                ]
                
                # スケジュール提案または健康関連の内容が含まれているかチェック
                for indicator in schedule_proposal_indicators:
                    if indicator in content:
                        schedule_proposal_content = content
                        self.logger.info(f"🔍 スケジュール提案発見: '{indicator}' が含まれる応答")
                        break
                
                if schedule_proposal_content:
                    break
        
        if not schedule_proposal_content:
            self.logger.warning("⚠️ 会話履歴にスケジュール提案が見つかりません")
            return None
        
        # Gemini APIを使用してスケジュール提案を構造化
        try:
            return await self._structure_schedule_proposal_with_gemini(schedule_proposal_content)
        except Exception as e:
            self.logger.warning(f"⚠️ Gemini APIスケジュール構造化に失敗、フォールバックを使用: {e}")
            return self._extract_schedule_from_text(schedule_proposal_content)

    def _extract_schedule_from_text(self, content: str) -> dict:
        """テキストからスケジュール情報を抽出（フォールバック）
        
        Args:
            content: メッセージ内容
            
        Returns:
            dict: 抽出されたスケジュール情報
        """
        # 基本的なスケジュールキーワードを検索
        schedule_keywords = ["診察", "検診", "健診", "予約", "受診", "通院", "ワクチン", "予防接種"]
        detected_schedules = [keyword for keyword in schedule_keywords if keyword in content]
        
        # デフォルトのスケジュール情報
        return {
            "title": detected_schedules[0] if detected_schedules else "健康関連の予定",
            "description": "AI提案による健康管理の予定",
            "event_type": "medical",
            "extracted_from": "text_fallback",
            "confidence": 0.5
        }

    async def _structure_schedule_proposal_with_gemini(self, schedule_proposal_content: str) -> dict:
        """Gemini APIを使用してスケジュール提案を構造化
        
        Args:
            schedule_proposal_content: スケジュール提案の自然言語レスポンス
            
        Returns:
            dict: 構造化されたスケジュール提案
        """
        try:
            # Vertex AI Gemini APIを使用してスケジュールデータを構造化
            import os

            import vertexai
            from vertexai.generative_models import GenerativeModel

            # Vertex AI初期化
            project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "blog-sample-381923")
            location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
            vertexai.init(project=project_id, location=location)
            
            model = GenerativeModel("gemini-2.5-flash")
            
            # 現在の日時情報を取得
            from datetime import datetime, timedelta
            import pytz
            
            # 日本時間での現在日時
            jst = pytz.timezone('Asia/Tokyo')
            now = datetime.now(jst)
            today = now.strftime('%Y-%m-%d')
            tomorrow = (now + timedelta(days=1)).strftime('%Y-%m-%d')
            current_time = now.strftime('%H:%M')
            
            # 構造化プロンプト
            structure_prompt = f"""
以下の健康・医療関連の会話レスポンスから、スケジュール・予定情報を抽出してください。
必ずJSON形式で応答し、以下の形式に従ってください：

**重要な日時変換ルール：**
- 現在日時: {now.strftime('%Y-%m-%d %H:%M')} (日本時間)
- 今日: {today}
- 明日: {tomorrow}
- 「明日」「明日の」→ {tomorrow}
- 「今日」「今日の」→ {today}
- 「10時」「午前10時」→ "10:00"
- 「午後2時」→ "14:00"
- 時間指定がない場合は "09:00" をデフォルトとする

{{
    "title": "予定のタイトル",
    "description": "予定の詳細説明",
    "event_type": "medical|school|outing|other",
    "suggested_date": "YYYY-MM-DD形式の具体的な日付（必須）",
    "suggested_time": "HH:MM形式の具体的な時刻（必須）",
    "location": "場所（病院・クリニック名など）",
    "notes": "注意事項やメモ",
    "reminder_needed": true,
    "confidence": 0.0-1.0の数値,
    "schedule_description": "スケジュールの簡潔な説明"
}}

**例：**
- 「明日の10時にキャップスクリニック」→ suggested_date: "{tomorrow}", suggested_time: "10:00"
- 「来週月曜日の予防接種」→ 次の月曜日の日付を計算
- 「午後2時の健診」→ suggested_time: "14:00"

スケジュール提案レスポンス:
{schedule_proposal_content}

JSONのみを返してください。suggested_dateとsuggested_timeは必ず具体的な値を設定してください。
"""

            # API呼び出し
            response = model.generate_content(structure_prompt)
            response_text = response.text.strip()
            
            # JSON部分を抽出
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                structured_data = json.loads(json_str)
                
                self.logger.info(f"✅ Gemini APIスケジュール構造化成功: {structured_data.get('title', '不明')}")
                return structured_data
            else:
                raise ValueError("JSONレスポンスが見つかりません")
                
        except Exception as e:
            self.logger.error(f"❌ Gemini APIスケジュール構造化エラー: {e}")
            # フォールバック: 基本的な構造化データを返す
            return {
                "title": "健康管理の予定",
                "description": "AI提案による健康・医療関連の予定",
                "event_type": "medical",
                "suggested_date": "",
                "suggested_time": "",
                "location": "",
                "notes": "Gemini API構造化に失敗しました",
                "reminder_needed": True,
                "confidence": 0.3,
                "schedule_description": "会話から抽出されたスケジュール",
                "original_content": schedule_proposal_content[:200] + "..." if len(schedule_proposal_content) > 200 else schedule_proposal_content
            }

    def _build_schedule_record_data(self, schedule_proposal: dict, child_info: dict, user_id: str) -> dict:
        """スケジュール記録データを構築
        
        Args:
            schedule_proposal: スケジュール提案結果
            child_info: 子供情報
            user_id: ユーザーID
            
        Returns:
            dict: スケジュール記録データ
        """
        
        title = schedule_proposal.get("title", "健康管理の予定")
        description = schedule_proposal.get("description", "AI提案による予定")
        
        # 日時設定（提案がない場合はデフォルト値）
        suggested_date = schedule_proposal.get("suggested_date", "")
        suggested_time = schedule_proposal.get("suggested_time", "")
        
        if suggested_date and suggested_time:
            start_datetime = f"{suggested_date}T{suggested_time}:00"
        elif suggested_date:
            start_datetime = f"{suggested_date}T10:00:00"  # デフォルト午前10時
        else:
            # 1週間後のデフォルト日時
            from datetime import datetime, timedelta
            default_datetime = datetime.now() + timedelta(days=7)
            start_datetime = default_datetime.strftime("%Y-%m-%dT%H:%M:%S")
        
        return {
            "user_id": user_id,
            "title": title,
            "description": description,
            "start_datetime": start_datetime,
            "event_type": schedule_proposal.get("event_type", "medical"),
            "location": schedule_proposal.get("location", ""),
            "notes": schedule_proposal.get("notes", ""),
            "reminder_minutes": 60 if schedule_proposal.get("reminder_needed", True) else 0,  # 1時間前リマインダー
            "confidence": schedule_proposal.get("confidence", 0.8)
        }

    async def _call_schedule_record_api(self, schedule_data: dict) -> dict:
        """スケジュール記録API呼び出し（実際のデータベース保存）
        
        Args:
            schedule_data: スケジュール記録データ
            
        Returns:
            dict: API応答結果
        """
        try:
            self.logger.info(f"📅 スケジュール記録API呼び出し: {schedule_data}")
            
            # Composition Rootから実際のScheduleManagementUseCaseを取得（重複初期化回避）
            if self._composition_root:
                schedule_usecase = self._composition_root._usecases.get("schedule_event_management")
            else:
                # フォールバック: 新規作成（非推奨パターン）
                from src.di_provider.composition_root import CompositionRootFactory
                composition_root = CompositionRootFactory.create()
                schedule_usecase = composition_root._usecases.get("schedule_event_management")
            
            if not schedule_usecase:
                self.logger.error("❌ ScheduleManagementUseCaseが利用できません")
                return {
                    "success": False,
                    "error": "スケジュール管理機能が利用できません"
                }
            
            # ScheduleEventUseCaseは辞書を直接受け取る仕様
            user_id = schedule_data.get("user_id", "default_user")
            event_data = {
                "title": schedule_data.get("title"),
                "description": schedule_data.get("description", ""),
                "start_datetime": schedule_data.get("start_datetime"),
                "end_datetime": schedule_data.get("end_datetime", ""),
                "event_type": schedule_data.get("event_type", "medical"),
                "location": schedule_data.get("location", ""),
                "notes": schedule_data.get("notes", ""),
                "reminder_minutes": schedule_data.get("reminder_minutes", 60)
            }
            
            # データベースに実際に保存
            schedule_response = await schedule_usecase.create_schedule_event(user_id, event_data)
            
            if not schedule_response.get("success"):
                error_msg = schedule_response.get("message", "スケジュール記録作成に失敗しました")
                self.logger.error(f"❌ スケジュール記録作成失敗: {error_msg}")
                return {
                    "success": False,
                    "error": error_msg
                }
            
            schedule_record = schedule_response.get("data")
            schedule_id = schedule_response.get("id") or (schedule_record.get("id") if schedule_record else "unknown")
            
            self.logger.info(f"✅ 実際のスケジュールデータベース保存成功: {schedule_id}")
            
            return {
                "success": True,
                "schedule_id": schedule_id,
                "message": "スケジュールがデータベースに正常に保存されました",
                "record": schedule_record
            }
            
        except Exception as e:
            self.logger.error(f"❌ スケジュール記録API呼び出しエラー: {e}")
            return {
                "success": False,
                "error": f"データベース保存エラー: {str(e)}"
            }
