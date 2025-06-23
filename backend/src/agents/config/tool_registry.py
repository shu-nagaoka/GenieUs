"""ツールレジストリ - 全ツールの一元管理"""

import logging
from typing import Dict, List, Callable, Optional

from google.adk.tools import FunctionTool, google_search

from src.di_provider.container import DIContainer


class ToolRegistry:
    """ツール一元管理レジストリ

    全てのツール（組み込み・カスタム）を登録・管理し、
    エージェント作成時に必要なツールを提供する
    """

    def __init__(self, container: DIContainer, logger: logging.Logger):
        self.container = container
        self.logger = logger
        self._tools: Dict[str, Callable[[], Optional[FunctionTool]]] = {}
        self._register_built_in_tools()
        self._register_custom_tools()

    def _register_built_in_tools(self) -> None:
        """組み込みツール登録"""
        try:
            # Google Search（ADK標準）
            self._tools["google_search"] = lambda: google_search
            self.logger.info("組み込みツール登録完了: google_search")

        except Exception as e:
            self.logger.error(f"組み込みツール登録エラー: {e}")

    def _register_custom_tools(self) -> None:
        """カスタムツール登録（ToolRegistry統一管理）"""
        try:
            # 画像分析ツール
            self._tools["image_analysis"] = self._safe_tool_getter(
                lambda: self._create_image_analysis_tool(), "image_analysis"
            )

            # 音声分析ツール
            self._tools["voice_analysis"] = self._safe_tool_getter(
                lambda: self._create_voice_analysis_tool(), "voice_analysis"
            )

            # ファイル管理ツール
            self._tools["file_management"] = self._safe_tool_getter(
                lambda: self._create_file_management_tool(), "file_management"
            )

            # 記録管理ツール
            self._tools["record_management"] = self._safe_tool_getter(
                lambda: self._create_record_management_tool(), "record_management"
            )

            # 子育て相談ツール（互換性のため残す）
            self._tools["childcare_consultation"] = self._safe_tool_getter(
                lambda: self._create_childcare_consultation_tool(), "childcare_consultation"
            )

            self.logger.info(f"カスタムツール登録完了: {len(self._tools) - 1}個")  # google_search除く

        except Exception as e:
            self.logger.error(f"カスタムツール登録エラー: {e}")

    def _safe_tool_getter(
        self, tool_factory: Callable[[], FunctionTool], tool_name: str
    ) -> Callable[[], Optional[FunctionTool]]:
        """ツール取得の安全なラッパー"""

        def get_tool() -> Optional[FunctionTool]:
            try:
                tool = tool_factory()
                if tool is not None:
                    self.logger.debug(f"ツール取得成功: {tool_name}")
                    return tool
                else:
                    self.logger.warning(f"ツールがNone: {tool_name}")
                    return None
            except Exception as e:
                self.logger.error(f"ツール取得エラー {tool_name}: {e}")
                return None

        return get_tool

    def get_tools(self, tool_names: List[str]) -> List[FunctionTool]:
        """指定されたツール名のツールを取得

        Args:
            tool_names: 取得したいツール名のリスト

        Returns:
            List[FunctionTool]: 有効なツールのリスト（Noneは除外）
        """
        tools = []

        for name in tool_names:
            if name in self._tools:
                tool = self._tools[name]()
                if tool is not None:
                    tools.append(tool)
                    self.logger.debug(f"ツール追加: {name}")
                else:
                    self.logger.warning(f"ツール取得失敗（None）: {name}")
            else:
                self.logger.warning(f"未登録ツール: {name}")
                self.logger.debug(f"利用可能ツール: {list(self._tools.keys())}")

        self.logger.info(f"ツール取得完了: {len(tools)}個 (要求: {len(tool_names)}個)")
        return tools

    def get_available_tools(self) -> List[str]:
        """利用可能なツール名一覧を取得"""
        return list(self._tools.keys())

    def is_tool_available(self, tool_name: str) -> bool:
        """指定されたツールが利用可能かチェック"""
        if tool_name not in self._tools:
            return False

        # 実際にツールを取得してNullチェック
        try:
            tool = self._tools[tool_name]()
            return tool is not None
        except Exception:
            return False

    def get_tool_info(self) -> Dict[str, Dict[str, any]]:
        """ツール情報の取得（デバッグ用）"""
        info = {}

        for tool_name in self._tools.keys():
            try:
                tool = self._tools[tool_name]()
                info[tool_name] = {"available": tool is not None, "type": type(tool).__name__ if tool else "None"}
                if tool is not None and hasattr(tool, "name"):
                    info[tool_name]["tool_name"] = tool.name
            except Exception as e:
                info[tool_name] = {"available": False, "error": str(e)}

        return info

    def register_external_tool(self, name: str, tool_factory: Callable[[], Optional[FunctionTool]]) -> None:
        """外部ツールの動的登録

        Args:
            name: ツール名
            tool_factory: ツールを作成する関数
        """
        self._tools[name] = tool_factory
        self.logger.info(f"外部ツール登録: {name}")

    # ========== ツール作成メソッド ==========

    def _create_image_analysis_tool(self) -> FunctionTool:
        """画像分析ツール作成"""
        from src.tools.image_analysis_tool import create_image_analysis_tool

        return create_image_analysis_tool(
            image_analysis_usecase=self.container.image_analysis_usecase(), logger=self.logger
        )

    def _create_voice_analysis_tool(self) -> FunctionTool:
        """音声分析ツール作成"""
        from src.tools.voice_analysis_tool import create_voice_analysis_tool

        return create_voice_analysis_tool(
            voice_analysis_usecase=self.container.voice_analysis_usecase(), logger=self.logger
        )

    def _create_file_management_tool(self) -> FunctionTool:
        """ファイル管理ツール作成"""
        from src.tools.file_management_tool import create_file_management_tool

        return create_file_management_tool(
            file_management_usecase=self.container.file_management_usecase(), logger=self.logger
        )

    def _create_record_management_tool(self) -> FunctionTool:
        """記録管理ツール作成"""
        from src.tools.record_management_tool import create_record_management_tool

        return create_record_management_tool(
            record_management_usecase=self.container.record_management_usecase(), logger=self.logger
        )
