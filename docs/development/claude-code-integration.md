# Claude Code統合・自律参照保証ガイド

Claude Codeが自律的にドキュメントを参照しながら開発することを保証するための仕組み

## 🎯 概要

### 課題
- Claude Codeが任意のタスクで適切なドキュメントを参照するか不明確
- 実装中にコーディング規約を忘れるリスク
- 品質基準違反の可能性

### 解決策
1. **CLAUDE.md強化** - タスク別参照マトリックス
2. **設定ファイル統合** - `.claude-config.json`による自動誘導
3. **テンプレート提供** - 規約準拠テンプレート
4. **自動チェック機能** - 実装時品質確認

## 📋 実装された保証機能

### 1. CLAUDE.md自律参照ガイド

#### **タスクタイプ別必須参照マトリックス**
```markdown
| タスク | 必須参照ドキュメント | チェックポイント |
|--------|---------------------|------------------|
| 🤖 新エージェント実装 | new-agent-creation.md + coding-standards.md | DI統合、ADK制約 |
| 🔧 新ツール開発 | new-tool-development.md + coding-standards.md | Protocol定義、薄いアダプター |
```

#### **実装前チェックリスト**
- [ ] 該当タスクの必須ドキュメントを読了
- [ ] Import文配置規約を理解
- [ ] 型アノテーション規約を理解
- [ ] エラーハンドリング戦略を理解

### 2. .claude-config.json設定

```json
{
  "mandatory_references": {
    "before_any_implementation": [
      "CLAUDE.md",
      "docs/development/coding-standards.md"
    ]
  },
  "task_specific_docs": {
    "agent_implementation": {
      "required": ["docs/guides/new-agent-creation.md"],
      "template": "docs/templates/agent_template.py"
    }
  }
}
```

### 3. テンプレートファイル

#### 提供テンプレート
- `docs/templates/agent_template.py` - エージェント実装テンプレート
- `docs/templates/tool_template.py` - ツール実装テンプレート

#### テンプレート特徴
- 規約準拠のコード構造
- Claude Code向けチェックポイント
- 実装時の注意事項

### 4. ドキュメント内Claude Code向け指示

各専門ドキュメントに以下を追加：
```markdown
## 🤖 Claude Code向け特別指示
**🚨 Claude Code実装者へ**: このドキュメントは実装前必読です。
```

## 🔄 自律参照フロー

### Claude Codeが受信するタスク例

```
ユーザー: "睡眠専門エージェントを実装してください"
```

### 期待される自律参照フロー

1. **CLAUDE.md確認**
   - タスクタイプ: 🤖 新エージェント実装
   - 必須参照: `new-agent-creation.md` + `coding-standards.md`

2. **設定ファイル確認**
   - `.claude-config.json`の`agent_implementation`セクション
   - テンプレート: `agent_template.py`

3. **必須ドキュメント読了**
   - `docs/guides/new-agent-creation.md` - 完全なガイド
   - `docs/development/coding-standards.md` - 規約確認

4. **テンプレート利用**
   - `docs/templates/agent_template.py`をベースに実装

5. **チェックリスト確認**
   - Import文配置
   - 型アノテーション
   - エラーハンドリング
   - DI統合

## ⚠️ 品質保証メカニズム

### 1. 実装前必須確認

Claude Codeは以下を**必ず**実行：
```markdown
実装開始前チェック:
□ 該当タスクの必須ドキュメントを参照済み
□ コーディング規約を理解済み
□ テンプレートを確認済み
□ チェックポイントを理解済み
```

### 2. 実装中継続確認

```markdown
コード実装中確認:
□ Import文がファイル先頭に配置されている
□ 型アノテーションが完備されている
□ エラーハンドリングが実装されている
□ レイヤー責務が守られている
```

### 3. 実装後品質確認

```markdown
完了前最終確認:
□ 絶対回避事項に該当していない
□ テンプレートのチェックポイントをクリア
□ lint/formatエラーなし
```

## 🛠️ 技術的実装

### A. Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

# Claude Code品質確認
echo "🤖 Claude Code実装品質チェック..."

# Import文配置確認
echo "📋 Import文配置確認..."
if grep -r "def.*:" backend/src/ | grep -A 10 "def" | grep -B 5 "import" > /dev/null; then
    echo "❌ エラー: 関数内でのimport文が検出されました"
    exit 1
fi

# 型アノテーション確認
echo "📋 型アノテーション確認..."
python_files=$(find backend/src -name "*.py" -type f)
for file in $python_files; do
    if grep -q "def.*(" "$file" && ! grep -q "def.*:.*->" "$file"; then
        echo "⚠️  警告: $file に型アノテーションなしの関数があります"
    fi
done

echo "✅ Claude Code品質チェック完了"
```

### B. VS Code設定

```json
{
  "claude.autoReference": true,
  "claude.mandatoryDocs": [
    "CLAUDE.md",
    "docs/development/coding-standards.md"
  ],
  "claude.taskTemplates": {
    "agent": "docs/templates/agent_template.py",
    "tool": "docs/templates/tool_template.py"
  }
}
```

### C. 自動リマインダー

ファイル作成時に自動挿入されるコメント：
```python
# 🚨 Claude Code: 実装前に以下を確認してください
# 📋 必須参照: docs/development/coding-standards.md
# 📋 タスク別ガイド: docs/guides/new-{type}-creation.md
# ✅ Import文先頭配置 ✅ 型アノテーション ✅ エラーハンドリング
```

## 📊 効果測定

### KPI指標

1. **参照率**: Claude Codeがドキュメントを参照した割合
2. **準拠率**: コーディング規約準拠の実装割合
3. **品質スコア**: lint/test/type checkの合格率
4. **手戻り率**: 実装後修正が必要だった割合

### 目標値

- 参照率: 100%（必須ドキュメント）
- 準拠率: 95%以上（Import文配置、型アノテーション）
- 品質スコア: 90%以上
- 手戻り率: 10%以下

## 🔧 トラブルシューティング

### よくある問題

#### Q: Claude Codeがドキュメントを参照しない
**A**: CLAUDE.mdの「Claude Code向け自律参照ガイド」セクションを強調

#### Q: コーディング規約違反が発生
**A**: .claude-config.jsonの"forbidden_patterns"を確認・強化

#### Q: テンプレートが使用されない
**A**: 該当タスクの設定で"template"プロパティを確認

## 🚀 今後の改善

### Phase 2: 高度な自動化

1. **Context7統合**: ライブラリドキュメント自動参照
2. **AI品質チェック**: 実装品質の自動評価
3. **学習機能**: Claude Codeの参照パターン学習

### Phase 3: エコシステム統合

1. **IDE統合**: リアルタイム品質フィードバック
2. **CI/CD統合**: 自動品質ゲート
3. **ダッシュボード**: 品質メトリクス可視化

---

**💡 重要**: この仕組みにより、Claude Codeは**自律的にドキュメント参照→規約準拠実装→品質確保**のサイクルを実現できます。