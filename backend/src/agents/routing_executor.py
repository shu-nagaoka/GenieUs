"""RoutingExecutor - ルーティング実行とエージェント実行管理

ルーティング決定に基づくエージェント実行、フォールバック処理を担当
"""

import logging
import time

from google.adk.runners import Runner
from google.genai.types import Content, Part

from src.agents.constants import (
    AGENT_DISPLAY_NAMES,
    AGENT_KEYWORDS,
    AGENT_RESPONSE_PATTERNS,
    ERROR_INDICATORS,
    FALLBACK_AGENT_PRIORITY,
    EXPLICIT_SEARCH_FLAGS,
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
        app_name: str = "GenieUs",
    ):
        """RoutingExecutor初期化

        Args:
            logger: DIコンテナから注入されるロガー
            routing_strategy: ルーティング戦略
            message_processor: メッセージプロセッサー
            app_name: アプリケーション名

        """
        self.logger = logger
        self.routing_strategy = routing_strategy
        self.message_processor = message_processor
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
                    message, 
                    conversation_history, 
                    family_info, 
                    has_image, 
                    message_type
                )
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

            # ルーティング妥当性チェック
            if not self._validate_routing_decision(message, selected_agent_type):
                self.logger.warning(f"⚠️ ルーティング妥当性警告: {selected_agent_type} が適切でない可能性")
                corrected_agent = self._auto_correct_routing(message, selected_agent_type)
                if corrected_agent != selected_agent_type:
                    self.logger.info(f"🔧 ルーティング自動修正: {selected_agent_type} → {corrected_agent}")
                    selected_agent_type = corrected_agent

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
        message_type: str = "text"
    ) -> str:
        """ルーティング決定"""
        if not self.routing_strategy:
            raise ValueError("ルーティング戦略が設定されていません")

        # 🖼️ **最優先**: 画像添付検出（戦略に依存しない）
        if has_image or message_type == "image":
            self.logger.info(f"🎯 RoutingExecutor: 画像添付最優先検出 has_image={has_image}, message_type={message_type} → image_specialist")
            return "image_specialist"

        # 🔍 **第2優先**: 明示的検索フラグの直接検出（戦略に依存しない）
        for search_flag in EXPLICIT_SEARCH_FLAGS:
            if search_flag.lower() in message.lower() or search_flag in message:
                self.logger.info(f"🎯 RoutingExecutor: 明示的検索フラグ第2優先検出 '{search_flag}' → search_specialist")
                return "search_specialist"

        agent_id, routing_info = self.routing_strategy.determine_agent(
            message, 
            conversation_history, 
            family_info, 
            has_image, 
            message_type
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
