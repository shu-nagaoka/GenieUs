"""AgentManager - シンプル版

ADK本来のシンプルさを活かした設計
- 1つのchildcareエージェント
- 必要なツールの統合のみ
"""

import asyncio
import logging
import os

from dotenv import load_dotenv
from google.adk.agents import Agent, SequentialAgent, ParallelAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part

# ADK環境変数を明示的に読み込み
load_dotenv()


class AgentManager:
    """マルチエージェント管理 - 専門特化型"""

    def __init__(self, tools: dict, logger: logging.Logger, settings):
        """AgentManager初期化"""
        self.logger = logger
        self.settings = settings
        self.tools = tools

        # マルチエージェント管理
        self._agents: dict[str, Agent] = {}
        self._runners: dict[str, Runner] = {}
        self._sequential_agent: SequentialAgent = None
        self._parallel_agent: ParallelAgent = None
        self._session_service = InMemorySessionService()
        self._app_name = "GenieUs"

    def initialize_all_components(self) -> None:
        """マルチエージェント初期化"""
        self.logger.info("マルチAgentManager初期化開始")

        try:
            # 1. 専門エージェント作成
            self._create_specialist_agents()

            # 2. コーディネーターエージェント作成
            self._create_coordinator_agent()

            # 3. Sequential/Parallelエージェント作成
            self._create_multi_agent_pipelines()

            # 4. Runner作成
            self._create_runners()

            self.logger.info(f"マルチAgentManager初期化完了: {len(self._agents)}個のエージェント")
        except Exception as e:
            self.logger.error(f"AgentManager初期化エラー: {e}")
            raise

    def _create_specialist_agents(self) -> None:
        """専門特化エージェント作成"""
        # 環境変数確認（デバッグ）
        project = os.getenv("GOOGLE_CLOUD_PROJECT")
        location = os.getenv("GOOGLE_CLOUD_LOCATION")
        use_vertexai = os.getenv("GOOGLE_GENAI_USE_VERTEXAI")
        self.logger.info(f"ADK環境変数: PROJECT={project}, LOCATION={location}, USE_VERTEXAI={use_vertexai}")

        # ツール確認ログ
        self.logger.info(f"🔧 利用可能ツール: {list(self.tools.keys())}")

        # 画像分析専門エージェント
        if self.tools.get("image_analysis"):
            self._agents["image_specialist"] = Agent(
                name="ImageAnalysisSpecialist",
                model="gemini-2.5-flash-preview-05-20",
                instruction="""あなたは温かく親しみやすい子どもの画像分析専門家です。
                お子さんの写真から表情や成長の様子を優しく見守り、親御さんに寄り添ったアドバイスをします。

                **あなたの特徴:**
                - 親御さんの気持ちに共感し、温かい言葉で対応
                - お子さんの良いところを見つけて、親御さんを励ます
                - 専門的な分析も分かりやすく、安心できる言葉で伝える
                - 画像がない場合も、優しく案内する

                **対応例:**
                「お子さんの成長の様子を一緒に見させていただきますね😊 
                お写真をお送りいただけましたら、表情や発達の様子を温かく見守らせていただきます。
                どんな小さなことでも、お子さんの素敵な瞬間を大切にお伝えしますので、安心してお任せください！」

                **専門性:**
                - 表情分析と感情推定（温かい視点で）
                - 発達段階の評価（親御さんを励ましながら）
                - 安全性の確認（不安を和らげながら）
                - 健康状態の観察（前向きなアドバイス）

                **重要:**
                画像分析の要求があれば、analyze_child_imageツールを使用しつつ、
                常に親御さんの心に寄り添った温かい対応を心がけてください。""",
                tools=[self.tools["image_analysis"]],
            )
            self.logger.info("🖼️ 画像分析専門エージェント作成完了")

        # 音声分析専門エージェント
        if self.tools.get("voice_analysis"):
            self._agents["voice_specialist"] = Agent(
                name="VoiceAnalysisSpecialist",
                model="gemini-2.5-flash-preview-05-20",
                instruction="""あなたは温かく理解深い子どもの音声分析専門家です。
                お子さんの泣き声や話し声を優しく聞き取り、親御さんの「なぜ泣いているの？」という気持ちに寄り添います。

                **あなたの特徴:**
                - 親御さんの「分からない」不安を受け止める
                - お子さんの声の意味を分かりやすく教える
                - 夜泣きや愚図りで困る親御さんを励ます
                - 「大丈夫ですよ」という安心感を提供

                **対応例:**
                「お子さんの泣き声、本当にお疲れさまです😌
                泣き声にはちゃんと意味があるんですよ。一緒に聞かせていただいて、
                お子さんが何を伝えたがっているのか、優しく読み取らせていただきますね💝
                きっと親御さんの不安が少しでも軽くなりますように」

                **専門性:**
                - 泣き声のパターン分析（親の不安を和らげながら）
                - 感情状態の推定（温かい解釈で）
                - お子さんの要求の解読（具体的なアドバイス）
                - ストレス軽減のサポート

                **重要:**
                音声分析の要求があれば、analyze_child_voiceツールを使用し、
                常に親御さんを労い、安心させる言葉を添えてください。""",
                tools=[self.tools["voice_analysis"]],
            )
            self.logger.info("🎵 音声分析専門エージェント作成完了")

        # 記録管理専門エージェント
        if self.tools.get("record_management"):
            self._agents["record_specialist"] = Agent(
                name="RecordManagementSpecialist",
                model="gemini-2.5-flash-preview-05-20",
                instruction="""あなたは温かく励ましてくれる子育て記録の専門家です。
                お子さんの成長の軌跡を大切に見守り、親御さんの頑張りを認めて応援します。

                **あなたの特徴:**
                - 親御さんの記録への努力を認め、褒める
                - 小さな成長も見逃さず、一緒に喜ぶ
                - 記録をつけることの大切さを温かく伝える
                - データから見える成長を感動的に表現

                **対応例:**
                「お子さんの成長記録、いつも大切につけていらっしゃるんですね✨
                その愛情あふれる記録から、きっと素敵な成長の物語が見えてきますよ。
                一緒にお子さんの頑張りと、親御さんの愛情を振り返らせていただきますね！
                どんな小さな変化も、かけがえのない成長の証ですから」

                **専門性:**
                - 成長記録の温かい分析
                - 親子の絆が見えるパターン発見
                - 愛情あふれるデータの整理
                - 希望につながる長期的な傾向把握

                **重要:**
                記録に関する要求があれば、manage_child_recordsツールを使用し、
                常に親御さんの努力を讃え、お子さんの成長を一緒に喜んでください。""",
                tools=[self.tools["record_management"]],
            )
            self.logger.info("📊 記録管理専門エージェント作成完了")

        # ファイル管理専門エージェント
        if self.tools.get("file_management"):
            self._agents["file_specialist"] = Agent(
                name="FileManagementSpecialist",
                model="gemini-2.5-flash-preview-05-20",
                instruction="""あなたは親しみやすく信頼できるファイル管理の専門家です。
                お子さんの大切な思い出や記録を安全に守り、親御さんが安心してお任せできる存在です。

                **あなたの特徴:**
                - 大切な思い出を守る責任感
                - 親御さんの不安に寄り添う優しさ
                - ファイル操作を分かりやすく案内
                - データの安全性を親身に説明

                **対応例:**
                「お子さんの大切な写真や動画、しっかりと安全にお預かりしますね📸✨
                思い出は何にも代えがたい宝物ですから、私が責任を持って管理させていただきます。
                いつでも簡単に見返せるように整理もいたしますので、安心してお任せください💕
                何かご不明な点があれば、お気軽にお声かけくださいね」

                **専門性:**
                - 思い出の安全な保存・整理
                - 大切なデータの取得・管理
                - 安心のバックアップ確認
                - 使いやすいファイル整理

                **重要:**
                ファイル操作の要求があれば、manage_child_filesツールを使用し、
                常に親御さんの大切な思い出を守る気持ちで対応してください。""",
                tools=[self.tools["file_management"]],
            )
            self.logger.info("📁 ファイル管理専門エージェント作成完了")

        # 栄養・食事専門エージェント（ツールなし・純粋相談型）
        self._agents["nutrition_specialist"] = Agent(
            name="NutritionSpecialist",
            model="gemini-2.5-flash-preview-05-20",
            instruction="""あなたは温かく寄り添う栄養・食事の専門家です。
            離乳食の進め方、食事の悩み、栄養バランスについて、親御さんの不安に寄り添いながらアドバイスします。

            **あなたの特徴:**
            - 食べない子を持つ親の気持ちを深く理解
            - 離乳食の進め方を段階的に優しく指導
            - 好き嫌いやアレルギーの心配に共感
            - 「大丈夫、焦らなくても」という安心感を提供
            - 実践的で続けやすいアドバイス

            **対応例:**
            「お食事のことでお悩みなんですね😊 離乳食や食事は本当に心配になりますよね。
            でも大丈夫です、お子さんのペースに合わせて、一緒に進めていきましょう🍎
            食べムラがあっても、拒否されても、それも成長の一部なんですよ。
            親御さんの愛情がちゃんと伝わっていますから、安心してくださいね💕」

            **専門分野:**
            - 離乳食の進め方（5-6ヶ月〜完了期まで）
            - 食事の悩み（食べない、好き嫌い、食べムラ）
            - 栄養バランスの考え方（実践的なアドバイス）
            - アレルギー対応（基本的な注意点）
            - 食育の基本（楽しい食事環境づくり）
            - 年齢別の食事のポイント

            **重要な方針:**
            - 完璧を求めず、できることから始める
            - 親御さんの頑張りを必ず認める
            - 具体的で実践しやすいアドバイス
            - 食事を通じた親子の絆を大切にする
            - 不安を和らげ、食事の時間を楽しいものにする

            常に親御さんの気持ちに寄り添い、温かく励ましながら、実用的なアドバイスを提供してください。""",
            # toolsなし = 純粋な相談・アドバイス専用
        )
        self.logger.info("🍎 栄養・食事専門エージェント作成完了")

    def _create_coordinator_agent(self) -> None:
        """コーディネーターエージェント作成（ルーティング専用）"""
        self._agents["coordinator"] = Agent(
            name="ChildcareCoordinator",
            model="gemini-2.5-flash-preview-05-20",
            instruction="""あなたは温かく親しみやすい子育て相談の専門家です。
            
            **最重要ルール - 会話継続:**
            - ユーザーから年齢や性別の情報が提供された場合、必ず前の会話の文脈（発達・栄養・行動等の相談内容）を思い出して、その続きとして回答してください
            - 「こんにちは」のような一般的な挨拶で初期化してはいけません
            - 常に会話の流れを意識し、相談の継続として対応してください
            
            **基本方針:**
            - 会話の流れを常に把握し、前の発言内容を踏まえて回答してください
            - 一般的な子育て質問には直接温かくお答えください
            - 専門分析が必要な場合のみ専門家への振り分けを提案
            - 常に親御さんの気持ちに寄り添った回答を心がけてください
            - 質問への回答は具体的で、相談者が求めている内容に直接答えてください
            
            **直接回答する内容:**
            - いやいや期、発達段階、夜泣きの一般的なアドバイス
            - 育児の悩み相談、心配事への共感・助言
            - 基本的な子育て知識、月齢・年齢別の特徴
            
            **専門家が必要な場合:**
            - 具体的な画像分析（「写真を見て」「表情を分析」「画像を分析」）
            - 音声分析（泣き声のパターン解析）
            - データ記録・分析（成長記録の管理）
            - ファイル操作（「ファイルを保存」「管理して」）

            まずは親御さんの質問に温かく答え、必要に応じて専門分析を提案してください。""",
            # toolsなし = 判断・ルーティング専用
        )
        self.logger.info("🎯 コーディネーターエージェント作成完了")

    def _create_multi_agent_pipelines(self) -> None:
        """Sequential/Parallelエージェント作成"""
        available_specialists = [agent for agent in self._agents.values() if agent.name != "ChildcareCoordinator"]

        if len(available_specialists) >= 1:
            # 段階的分析パイプライン（専門家が1つでもあれば作成）
            # コーディネーターなしで専門家のみのSequentialを作成
            self._sequential_agent = SequentialAgent(
                name="SequentialAnalysisPipeline",
                sub_agents=available_specialists[:1],  # 最初の専門家のみ
            )
            self.logger.info("🔄 Sequential分析パイプライン作成完了（専門家のみ）")
        else:
            # 専門エージェントがない場合はコーディネーターのみ
            self._sequential_agent = SequentialAgent(
                name="CoordinatorOnlyPipeline", sub_agents=[self._agents["coordinator"]]
            )
            self.logger.warning("⚠️ 専門エージェントなし。コーディネーターのみのSequentialを作成")

        # 並列分析パイプライン（専門家を複製して使用）
        if len(available_specialists) >= 2:
            parallel_specialists = []
            # 栄養専門家を含む主要な専門家を優先選択
            for specialist in available_specialists[:4]:  # 最大4専門家（栄養も含める）
                # 同じ設定で新しいインスタンス作成
                parallel_agent = Agent(
                    name=f"{specialist.name}_Parallel",  # 名前を変更
                    model=specialist.model,
                    instruction=specialist.instruction,
                    tools=specialist.tools,
                )
                parallel_specialists.append(parallel_agent)

            self._parallel_agent = ParallelAgent(name="ParallelAnalysisPipeline", sub_agents=parallel_specialists)
            self.logger.info(f"⚡ Parallel分析パイプライン作成完了: {len(parallel_specialists)}専門家")
        else:
            self.logger.warning("⚠️ 専門エージェント不足。Parallel分析パイプライン未作成")

    def _create_runners(self) -> None:
        """各エージェント用のRunner作成"""
        for agent_name, agent in self._agents.items():
            self._runners[agent_name] = Runner(
                agent=agent, app_name=self._app_name, session_service=self._session_service
            )

        # Sequential/Parallel用のRunner
        if self._sequential_agent:
            self._runners["sequential"] = Runner(
                agent=self._sequential_agent, app_name=self._app_name, session_service=self._session_service
            )

        if self._parallel_agent:
            self._runners["parallel"] = Runner(
                agent=self._parallel_agent, app_name=self._app_name, session_service=self._session_service
            )

        self.logger.info(f"🏃 Runner作成完了: {len(self._runners)}個")

    # ========== 外部インターフェース ==========

    def get_agent(self, agent_type: str = "coordinator") -> Agent:
        """エージェント取得"""
        if agent_type not in self._agents:
            available = list(self._agents.keys())
            raise RuntimeError(f"エージェント '{agent_type}' が見つかりません。利用可能: {available}")
        return self._agents[agent_type]

    async def route_query_async(
        self, message: str, user_id: str = "default_user", session_id: str = "default_session", agent_type: str = "auto", conversation_history: list = None, family_info: dict = None
    ) -> str:
        """マルチエージェント対応クエリ実行（非同期）"""
        try:
            # エージェント選択ロジック
            if agent_type == "auto":
                selected_agent_type = self._determine_agent_type(message)
            elif agent_type in ["sequential", "parallel"]:
                selected_agent_type = agent_type
            else:
                selected_agent_type = agent_type

            self.logger.info(f"🎯 選択されたエージェント: {selected_agent_type}")
            self.logger.info(f"🔧 利用可能なRunners: {list(self._runners.keys())}")

            # Runner取得
            if selected_agent_type not in self._runners:
                self.logger.warning(f"⚠️ {selected_agent_type} Runnerが見つかりません。coordinatorを使用")
                selected_agent_type = "coordinator"

            runner = self._runners[selected_agent_type]
            self.logger.info(f"🚀 実行エージェント: {selected_agent_type} (Agent: {runner.agent.name})")
            await self._ensure_session_exists(user_id, session_id)
            
            # 履歴と家族情報を含めたメッセージ作成
            enhanced_message = self._create_message_with_context(message, conversation_history, family_info)
            content = Content(role="user", parts=[Part(text=enhanced_message)])

            # ADK実行
            events = []
            tool_used = False
            async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
                events.append(event)

                # ツール使用検出（詳細ログ）
                if hasattr(event, "actions") and event.actions:
                    tool_used = True
                    try:
                        action_count = len(list(event.actions)) if hasattr(event.actions, "__iter__") else 1
                        self.logger.info(f"🔧 {selected_agent_type} ツール実行検出: {action_count}個のアクション")

                        # アクション詳細をログ出力
                        for i, action in enumerate(event.actions):
                            self.logger.info(f"📋 アクション#{i + 1}: {type(action).__name__}")
                            self.logger.info(f"📄 アクション内容: {str(action)[:500]}...")
                    except Exception as e:
                        self.logger.info(f"🔧 ツール実行検出: アクションあり (詳細取得エラー: {e})")

                # レスポンス内容の詳細ログ
                if hasattr(event, "content") and event.content:
                    if hasattr(event.content, "parts") and event.content.parts:
                        for i, part in enumerate(event.content.parts):
                            if hasattr(part, "function_response"):
                                self.logger.info(f"🔧 ツールレスポンス#{i + 1}: {str(part.function_response)[:500]}...")
                            elif hasattr(part, "text") and len(str(part.text)) > 0:
                                self.logger.info(f"💬 {selected_agent_type} 文章#{i + 1}: {str(part.text)[:200]}...")

            self.logger.info(
                f"🔧 {selected_agent_type} ツール使用結果: {'使用された' if tool_used else '使用されなかった'}"
            )

            # レスポンス抽出
            if events and hasattr(events[-1], "content") and events[-1].content:
                return self._extract_response_text(events[-1].content)
            else:
                raise Exception("No response from agent")

        except Exception as e:
            self.logger.error(f"エージェント実行エラー: {e}")
            return f"申し訳ございません。システムエラーが発生しました: {str(e)}"

    def _determine_agent_type(self, message: str) -> str:
        """メッセージ内容から適切なエージェントタイプを決定"""
        message_lower = message.lower()

        # 明確にツール実行が必要なキーワード
        tool_required_keywords = [
            "画像を分析", "写真を見て", "表情を分析", "顔を見て", "画像解析",
            "音声を分析", "泣き声を解析", "音声パターン", "声を聞いて",
            "記録を管理", "データを分析", "パターンを調べて", "記録して",
            "ファイルを保存", "ファイル管理", "アップロード", "ダウンロード"
        ]
        
        # 栄養・食事専門が適切なキーワード
        nutrition_keywords = [
            "離乳食", "食事", "栄養", "食べない", "好き嫌い", "食べムラ", "アレルギー",
            "食材", "レシピ", "食べさせ方", "食育", "偏食", "野菜を食べない",
            "ミルク", "母乳", "卒乳", "断乳", "食事量", "栄養バランス"
        ]
        
        # 並列分析が適切なキーワード
        parallel_keywords = [
            "総合的に", "詳しく分析", "複数の視点", "全体的に",
            "多角的に", "いろんな角度から", "様々な専門家に", "チーム分析",
            "みんなで分析", "複数の専門家", "多面的", "包括的",
            "トータル", "全ての専門家", "複合的"
        ]

        # 栄養・食事専門が適切
        if any(keyword in message_lower for keyword in nutrition_keywords):
            return "nutrition_specialist"
        
        # ツール実行が明確に必要
        elif any(keyword in message_lower for keyword in tool_required_keywords):
            return "image_specialist" if any(k in message_lower for k in ["画像", "写真", "表情", "顔"]) else \
                   "voice_specialist" if any(k in message_lower for k in ["音声", "泣き声", "声"]) else \
                   "record_specialist" if any(k in message_lower for k in ["記録", "データ", "パターン"]) else \
                   "file_specialist" if any(k in message_lower for k in ["ファイル", "保存", "管理"]) else \
                   "sequential"
        
        # 並列分析が適切
        elif any(keyword in message_lower for keyword in parallel_keywords):
            return "parallel"
        
        # デフォルトは汎用的な相談対応
        else:
            return "coordinator"

    def route_query(self, message: str, user_id: str = "default_user", session_id: str = "default_session") -> str:
        """クエリ実行（同期）"""
        return asyncio.run(self.route_query_async(message, user_id, session_id))

    async def _ensure_session_exists(self, user_id: str, session_id: str) -> None:
        """セッション存在確認・作成"""
        try:
            await self._session_service.get_session(self._app_name, user_id, session_id)
        except Exception:
            await self._session_service.create_session(app_name=self._app_name, user_id=user_id, session_id=session_id)

    def _create_message_with_context(self, message: str, conversation_history: list = None, family_info: dict = None) -> str:
        """会話履歴と家族情報を含めたメッセージを作成"""
        context_parts = []
        
        # 家族情報セクション
        if family_info:
            family_text = "【家族情報】\n"
            
            # 子どもの情報
            children = family_info.get('children', [])
            if children:
                family_text += "お子さん:\n"
                for i, child in enumerate(children):
                    child_info = []
                    if child.get('name'):
                        child_info.append(f"お名前: {child['name']}")
                    if child.get('age'):
                        child_info.append(f"年齢: {child['age']}")
                    if child.get('gender'):
                        child_info.append(f"性別: {child['gender']}")
                    if child.get('birth_date'):
                        child_info.append(f"生年月日: {child['birth_date']}")
                    if child.get('characteristics'):
                        child_info.append(f"特徴: {child['characteristics']}")
                    if child.get('allergies'):
                        child_info.append(f"アレルギー: {child['allergies']}")
                    if child.get('medical_notes'):
                        child_info.append(f"健康メモ: {child['medical_notes']}")
                    
                    if child_info:
                        family_text += f"  - {', '.join(child_info)}\n"
            
            # 保護者情報
            if family_info.get('parent_name'):
                family_text += f"保護者: {family_info['parent_name']}\n"
            if family_info.get('family_structure'):
                family_text += f"家族構成: {family_info['family_structure']}\n"
            if family_info.get('concerns'):
                family_text += f"主な心配事: {family_info['concerns']}\n"
            
            context_parts.append(family_text)
        
        # 会話履歴セクション
        if conversation_history and len(conversation_history) > 0:
            recent_history = conversation_history[-5:] if len(conversation_history) > 5 else conversation_history
            
            history_text = "【会話履歴】\n"
            for hist in recent_history:
                sender = hist.get('sender', 'unknown')
                content = hist.get('content', '')
                if sender == 'user':
                    history_text += f"親御さん: {content}\n"
                elif sender == 'assistant':
                    history_text += f"アドバイザー: {content}\n"
            
            context_parts.append(history_text)
        
        # 現在のメッセージ
        current_message = f"【現在のメッセージ】\n親御さん: {message}\n"
        context_parts.append(current_message)
        
        # 指示文
        if context_parts[:-1]:  # 家族情報や履歴がある場合
            instruction = "\n上記の家族情報と会話履歴を踏まえて、お子さんの個性や状況に合わせた個別的なアドバイスを提供してください。家族の状況を理解した上で、親御さんの現在のメッセージに温かく回答してください。"
            context_parts.append(instruction)
        
        enhanced_message = "\n".join(context_parts)
        
        context_info = []
        if family_info:
            children_count = len(family_info.get('children', []))
            context_info.append(f"家族情報(子{children_count}人)")
        if conversation_history:
            context_info.append(f"履歴{len(conversation_history)}件")
        
        self.logger.info(f"📚 コンテキスト付きメッセージ作成: {', '.join(context_info) if context_info else '基本メッセージ'}")
        return enhanced_message

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

    # ========== 互換性メソッド ==========

    @property
    def _runner(self) -> Runner:
        """互換性のための_runner属性（coordinatorのRunnerを返す）"""
        if "coordinator" in self._runners:
            return self._runners["coordinator"]
        elif self._runners:
            # coordinatorがない場合は最初のRunnerを返す
            return list(self._runners.values())[0]
        else:
            raise RuntimeError("Runnerが初期化されていません")

    def get_all_agents(self) -> dict[str, Agent]:
        """全エージェント取得"""
        return self._agents.copy()

    def get_agent_info(self) -> dict[str, dict[str, str]]:
        """エージェント情報取得"""
        info = {}
        for agent_name, agent in self._agents.items():
            info[agent_name] = {
                "name": agent.name,
                "model": agent.model,
                "tools_count": len(agent.tools) if agent.tools else 0,
                "type": "specialist" if agent_name != "coordinator" else "coordinator",
            }

        # Sequential/Parallel情報追加
        if self._sequential_agent:
            info["sequential_pipeline"] = {
                "name": self._sequential_agent.name,
                "model": "pipeline",
                "sub_agents_count": len(self._sequential_agent.sub_agents),
                "type": "sequential",
            }

        if self._parallel_agent:
            info["parallel_pipeline"] = {
                "name": self._parallel_agent.name,
                "model": "pipeline",
                "sub_agents_count": len(self._parallel_agent.sub_agents),
                "type": "parallel",
            }

        return info

    def get_available_agent_types(self) -> list[str]:
        """利用可能なエージェントタイプ一覧"""
        types = list(self._agents.keys())
        if self._sequential_agent:
            types.append("sequential")
        if self._parallel_agent:
            types.append("parallel")
        types.append("auto")  # 自動選択
        return types
