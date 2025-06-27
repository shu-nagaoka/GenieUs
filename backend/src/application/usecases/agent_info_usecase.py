"""エージェント情報管理UseCase

コーディング規約準拠:
- Import文ファイル先頭配置
- 型アノテーション完備
- 統一戻り値形式
- DI注入ロガー
"""

import logging
from typing import Any


class AgentInfoUseCase:
    """エージェント情報管理のビジネスロジック
    
    専門エージェント情報の取得、管理機能を提供
    """

    def __init__(self, logger: logging.Logger) -> None:
        """Args:
        logger: ロガー（DIコンテナから注入）

        """
        self.logger = logger

        # ビジネスロジック: 専門家マスターデータ
        self._specialist_master = self._initialize_specialist_master()

    def get_specialist_info(self, agent_type: str) -> dict[str, Any]:
        """エージェントタイプから専門家情報を取得

        Args:
            agent_type: エージェントタイプ

        Returns:
            Dict[str, Any]: 専門家情報

        """
        try:
            self.logger.info(f"専門家情報取得開始: agent_type={agent_type}")

            # ビジネスロジック: 専門家情報検索
            specialist_info = self._find_specialist_by_type(agent_type)

            # ビジネスロジック: 情報の検証・正規化
            validated_info = self._validate_specialist_info(specialist_info)

            self.logger.info(f"専門家情報取得完了: {validated_info['name']}")

            return {
                "success": True,
                "data": validated_info,
                "agent_type": agent_type,
            }

        except Exception as e:
            self.logger.error(f"専門家情報取得エラー: agent_type={agent_type}, error={e}")
            return {
                "success": False,
                "error": str(e),
                "data": self._get_default_specialist_info(),
            }

    def get_all_specialists(self) -> dict[str, Any]:
        """全専門家情報を取得

        Returns:
            Dict[str, Any]: 全専門家情報一覧

        """
        try:
            self.logger.info("全専門家情報取得開始")

            specialists = []
            for agent_type, info in self._specialist_master.items():
                specialists.append({
                    "agent_type": agent_type,
                    **info,
                })

            self.logger.info(f"全専門家情報取得完了: {len(specialists)}件")

            return {
                "success": True,
                "data": specialists,
                "total_count": len(specialists),
            }

        except Exception as e:
            self.logger.error(f"全専門家情報取得エラー: {e}")
            return {
                "success": False,
                "error": str(e),
                "data": [],
            }

    def get_specialists_by_category(self, category: str) -> dict[str, Any]:
        """カテゴリ別専門家情報を取得

        Args:
            category: 専門家カテゴリ (basic_tools, core_specialists, multi_agent等)

        Returns:
            Dict[str, Any]: カテゴリ別専門家情報

        """
        try:
            self.logger.info(f"カテゴリ別専門家情報取得開始: category={category}")

            # ビジネスロジック: カテゴリ分類
            categorized_specialists = self._categorize_specialists_by_type(category)

            self.logger.info(f"カテゴリ別専門家情報取得完了: {len(categorized_specialists)}件")

            return {
                "success": True,
                "data": categorized_specialists,
                "category": category,
                "count": len(categorized_specialists),
            }

        except Exception as e:
            self.logger.error(f"カテゴリ別専門家情報取得エラー: category={category}, error={e}")
            return {
                "success": False,
                "error": str(e),
                "data": [],
            }

    def _initialize_specialist_master(self) -> dict[str, dict[str, Any]]:
        """専門家マスターデータ初期化（ビジネスロジック）"""
        return {
            # 基本エージェント（ツール利用系）
            "image_specialist": {
                "name": "画像解析のジーニー",
                "description": "お子さんの写真から表情や成長を優しく分析",
                "tools": ["analyze_child_image", "image_processing"],
                "category": "basic_tools",
            },
            "voice_specialist": {
                "name": "音声解析のジーニー",
                "description": "泣き声や話し声から気持ちを理解",
                "tools": ["analyze_child_voice", "voice_processing"],
                "category": "basic_tools",
            },
            "record_specialist": {
                "name": "記録分析のジーニー",
                "description": "成長記録から大切なパターンを発見",
                "tools": ["manage_child_records", "data_analysis"],
                "category": "basic_tools",
            },
            "file_specialist": {
                "name": "ファイル管理のジーニー",
                "description": "大切な思い出を安全に保存・整理",
                "tools": ["manage_child_files", "file_organization"],
                "category": "basic_tools",
            },

            # 15専門エージェント
            "coordinator": {
                "name": "子育て相談のジーニー",
                "description": "温かく寄り添う総合的な子育てサポート",
                "tools": ["childcare_consultation", "general_advice"],
                "category": "core_specialists",
            },
            "nutrition_specialist": {
                "name": "栄養・食事のジーニー",
                "description": "離乳食や食事の悩みに温かく寄り添い",
                "tools": ["nutrition_advice", "meal_planning"],
                "category": "core_specialists",
            },
            "sleep_specialist": {
                "name": "睡眠のジーニー",
                "description": "夜泣きや寝かしつけの悩みを優しく解決",
                "tools": ["sleep_analysis", "bedtime_guidance"],
                "category": "core_specialists",
            },
            "development_specialist": {
                "name": "発達支援のジーニー",
                "description": "お子さんの発達を温かく見守りサポート",
                "tools": ["development_assessment", "growth_support"],
                "category": "core_specialists",
            },
            "health_specialist": {
                "name": "健康管理のジーニー",
                "description": "体調や健康の心配事に寄り添い",
                "tools": ["health_monitoring", "medical_guidance"],
                "category": "core_specialists",
            },
            "behavior_specialist": {
                "name": "行動・しつけのジーニー",
                "description": "イヤイヤ期や生活習慣を優しくサポート",
                "tools": ["behavior_analysis", "parenting_tips"],
                "category": "core_specialists",
            },
            "play_learning_specialist": {
                "name": "遊び・学習のジーニー",
                "description": "年齢に合った遊びと学習を提案",
                "tools": ["educational_activities", "play_suggestions"],
                "category": "core_specialists",
            },
            "safety_specialist": {
                "name": "安全・事故防止のジーニー",
                "description": "家庭での安全対策と事故防止をサポート",
                "tools": ["safety_assessment", "accident_prevention"],
                "category": "core_specialists",
            },
            "mental_care_specialist": {
                "name": "心理・メンタルケアのジーニー",
                "description": "親子の心のケアと支援",
                "tools": ["mental_support", "stress_management"],
                "category": "core_specialists",
            },
            "work_life_specialist": {
                "name": "仕事両立のジーニー",
                "description": "仕事と育児の両立を温かくサポート",
                "tools": ["work_life_balance", "childcare_planning"],
                "category": "core_specialists",
            },
            "special_support_specialist": {
                "name": "特別支援・療育のジーニー",
                "description": "特別な支援が必要なお子さんと家族をサポート",
                "tools": ["special_education", "therapeutic_support"],
                "category": "core_specialists",
            },
            "family_relationship_specialist": {
                "name": "家族関係のジーニー",
                "description": "家族の絆を深め、関係性の悩みを温かくサポート",
                "tools": ["family_support", "relationship_guidance"],
                "category": "core_specialists",
            },
            "search_specialist": {
                "name": "検索のジーニー",
                "description": "最新の子育て情報を検索してお届け",
                "tools": ["web_search", "information_gathering"],
                "category": "core_specialists",
            },
            "administration_specialist": {
                "name": "窓口・申請のジーニー",
                "description": "自治体手続きや申請をスムーズにサポート",
                "tools": ["application_support", "administrative_guidance"],
                "category": "core_specialists",
            },
            "outing_event_specialist": {
                "name": "おでかけ・イベントのジーニー",
                "description": "楽しいお出かけ先やイベント情報をご提案",
                "tools": ["web_search", "event_planning", "outing_recommendations"],
                "category": "core_specialists",
            },

            # マルチエージェント
            "sequential": {
                "name": "連携分析のジーニー",
                "description": "複数の専門家が順番に詳しく分析",
                "tools": ["sequential_analysis", "multi_step_processing"],
                "category": "multi_agent",
            },
            "parallel": {
                "name": "総合分析のジーニー",
                "description": "複数の専門家が同時に多角的に分析",
                "tools": ["parallel_analysis", "comprehensive_evaluation"],
                "category": "multi_agent",
            },
        }

    def _find_specialist_by_type(self, agent_type: str) -> dict[str, Any]:
        """専門家タイプによる検索（ビジネスロジック）"""
        return self._specialist_master.get(agent_type, self._get_default_specialist_info())

    def _validate_specialist_info(self, specialist_info: dict[str, Any]) -> dict[str, Any]:
        """専門家情報の検証・正規化（ビジネスロジック）"""
        # 必須フィールドの確認
        required_fields = ["name", "description", "tools"]
        for field in required_fields:
            if field not in specialist_info:
                specialist_info[field] = self._get_default_value_for_field(field)

        # カテゴリ情報の確保
        if "category" not in specialist_info:
            specialist_info["category"] = "unknown"

        return specialist_info

    def _categorize_specialists_by_type(self, category: str) -> list[dict[str, Any]]:
        """カテゴリ別専門家分類（ビジネスロジック）"""
        categorized = []
        for agent_type, info in self._specialist_master.items():
            if info.get("category") == category:
                categorized.append({
                    "agent_type": agent_type,
                    **info,
                })
        return categorized

    def _get_default_specialist_info(self) -> dict[str, Any]:
        """デフォルト専門家情報（フォールバック）"""
        return {
            "name": "子育てサポートのジーニー",
            "description": "温かく寄り添う子育てサポート",
            "tools": ["general_support"],
            "category": "default",
        }

    def _get_default_value_for_field(self, field: str) -> Any:
        """フィールドのデフォルト値取得"""
        defaults = {
            "name": "子育てサポートのジーニー",
            "description": "温かく寄り添う子育てサポート",
            "tools": ["general_support"],
            "category": "unknown",
        }
        return defaults.get(field, "")
