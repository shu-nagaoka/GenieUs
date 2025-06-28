#!/usr/bin/env python3
"""
Claude Code実装品質自動チェックスクリプト
実装後にこのスクリプトを実行してClaude Codeの参照・準拠状況を確認
"""

import os
import re
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple


def check_import_placement(file_path: str) -> Tuple[bool, List[str]]:
    """Import文の配置をチェック"""
    violations = []

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 関数内import検出
    function_import_pattern = r"def\s+\w+.*?:\s*\n(.*?)\n.*?import\s+"
    matches = re.findall(function_import_pattern, content, re.DOTALL)

    if matches:
        violations.append(f"関数内でのimport文検出: {file_path}")

    return len(violations) == 0, violations


def check_type_annotations(file_path: str) -> Tuple[bool, List[str]]:
    """型アノテーションをチェック"""
    violations = []

    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for i, line in enumerate(lines, 1):
        # 関数定義を検出
        if re.match(r"\s*def\s+\w+.*\(.*\):", line.strip()):
            # 戻り値の型アノテーションがあるかチェック
            if "->" not in line and "__init__" not in line:
                violations.append(
                    f"{file_path}:{i} - 型アノテーションなし: {line.strip()}"
                )

    return len(violations) == 0, violations


def check_error_handling(file_path: str) -> Tuple[bool, List[str]]:
    """エラーハンドリングをチェック"""
    violations = []

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 外部API呼び出しパターン
    api_patterns = [
        r"requests\.\w+\(",
        r"http\w*\.",
        r"fetch\(",
        r"axios\.",
    ]

    for pattern in api_patterns:
        matches = re.findall(pattern, content)
        if matches:
            # try-except内にあるかチェック
            if "try:" not in content or "except" not in content:
                violations.append(
                    f"外部API呼び出しでエラーハンドリング不足: {file_path}"
                )

    return len(violations) == 0, violations


def check_di_violations(file_path: str) -> Tuple[bool, List[str]]:
    """DI違反をチェック"""
    violations = []

    if "main.py" in file_path:
        return True, []  # main.pyは除外

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # get_container直接呼び出し検出
    if "get_container()" in content:
        violations.append(f"DIコンテナ直接呼び出し検出: {file_path}")

    return len(violations) == 0, violations


def analyze_python_files(directory: str) -> Dict[str, any]:
    """Python ファイルの品質分析"""
    results = {
        "total_files": 0,
        "passed_files": 0,
        "violations": {
            "import_placement": [],
            "type_annotations": [],
            "error_handling": [],
            "di_violations": [],
        },
    }

    python_files = list(Path(directory).rglob("*.py"))
    results["total_files"] = len(python_files)

    for file_path in python_files:
        file_str = str(file_path)

        # チェック実行
        import_ok, import_violations = check_import_placement(file_str)
        type_ok, type_violations = check_type_annotations(file_str)
        error_ok, error_violations = check_error_handling(file_str)
        di_ok, di_violations = check_di_violations(file_str)

        # 結果集計
        results["violations"]["import_placement"].extend(import_violations)
        results["violations"]["type_annotations"].extend(type_violations)
        results["violations"]["error_handling"].extend(error_violations)
        results["violations"]["di_violations"].extend(di_violations)

        if import_ok and type_ok and error_ok and di_ok:
            results["passed_files"] += 1

    return results


def check_claude_config_exists() -> bool:
    """Claude Code設定ファイルの存在確認"""
    return os.path.exists(".claude-config.json")


def check_template_usage() -> Dict[str, bool]:
    """テンプレート使用状況確認"""
    template_dir = Path("docs/templates")

    return {
        "agent_template_exists": (template_dir / "agent_template.py").exists(),
        "tool_template_exists": (template_dir / "tool_template.py").exists(),
    }


def check_documentation_links() -> Dict[str, bool]:
    """ドキュメントリンクの有効性確認"""
    required_docs = [
        "docs/development/coding-standards.md",
        "docs/guides/new-agent-creation.md",
        "docs/guides/new-tool-development.md",
        "docs/architecture/overview.md",
    ]

    return {doc: os.path.exists(doc) for doc in required_docs}


def main():
    """メイン実行関数"""
    print("🤖 Claude Code実装品質チェック開始\n")

    # 1. 設定ファイル確認
    print("📋 1. 設定ファイル確認")
    config_exists = check_claude_config_exists()
    print(f"   .claude-config.json: {'✅' if config_exists else '❌'}")

    # 2. テンプレート確認
    print("\n📋 2. テンプレート確認")
    templates = check_template_usage()
    for template, exists in templates.items():
        print(f"   {template}: {'✅' if exists else '❌'}")

    # 3. ドキュメントリンク確認
    print("\n📋 3. 必須ドキュメント確認")
    docs = check_documentation_links()
    for doc, exists in docs.items():
        print(f"   {doc}: {'✅' if exists else '❌'}")

    # 4. コード品質分析
    print("\n📋 4. Python コード品質分析")
    backend_results = analyze_python_files("backend/src")

    total = backend_results["total_files"]
    passed = backend_results["passed_files"]
    compliance_rate = (passed / total * 100) if total > 0 else 0

    print(f"   分析ファイル数: {total}")
    print(f"   準拠ファイル数: {passed}")
    print(f"   準拠率: {compliance_rate:.1f}%")

    # 5. 違反詳細表示
    print("\n📋 5. 品質違反詳細")
    violations = backend_results["violations"]

    for category, issues in violations.items():
        if issues:
            print(f"\n   ❌ {category}:")
            for issue in issues[:5]:  # 最大5件表示
                print(f"      - {issue}")
            if len(issues) > 5:
                print(f"      ... その他{len(issues) - 5}件")
        else:
            print(f"   ✅ {category}: 違反なし")

    # 6. 総合評価
    print(f"\n{'=' * 50}")
    print("📊 総合評価")

    if compliance_rate >= 90:
        print("🎉 優秀: Claude Code実装品質基準を満たしています")
    elif compliance_rate >= 70:
        print("⚠️  改善必要: いくつかの品質問題があります")
    else:
        print("❌ 要修正: 重大な品質問題があります")

    print(f"目標準拠率: 95% | 現在準拠率: {compliance_rate:.1f}%")

    # 7. 推奨アクション
    print(f"\n📋 推奨アクション")
    if not config_exists:
        print("   - .claude-config.json を設定してください")

    if violations["import_placement"]:
        print("   - Import文をファイル先頭に移動してください")

    if violations["type_annotations"]:
        print("   - 関数に型アノテーションを追加してください")

    print("\n🔗 参考ドキュメント:")
    print("   - docs/development/coding-standards.md")
    print("   - docs/development/claude-code-integration.md")


if __name__ == "__main__":
    main()
